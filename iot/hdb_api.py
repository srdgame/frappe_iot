# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import requests
from frappe import throw, msgprint, _
from frappe.model.document import Document
from iot.doctype.iot_device.iot_device import IOTDevice
from iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings
from cloud.cloud.doctype.cloud_settings.cloud_settings import CloudSettings
from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups as _list_user_groups
from cloud.cloud.doctype.cloud_company.cloud_company import list_user_companies
from frappe.utils import cint


def valid_auth_code(auth_code=None):
	auth_code = auth_code or frappe.get_request_header("HDB-AuthorizationCode")
	if not auth_code:
		throw(_("HDB-AuthorizationCode is required in HTTP Header!"))
	frappe.logger(__name__).debug(_("HDB-AuthorizationCode as {0}").format(auth_code))

	user = IOTHDBSettings.get_on_behalf(auth_code)
	if not user:
		throw(_("Authorization Code is incorrect!"))
	# form dict keeping
	form_dict = frappe.local.form_dict
	frappe.set_user(user)
	frappe.local.form_dict = form_dict


@frappe.whitelist(allow_guest=True)
def list_companies():
	valid_auth_code()
	return frappe.get_all("Cloud Company",
						fields=["name", "comp_name", "full_name", "enabled", "admin", "domain", "creation", "modified"])


@frappe.whitelist(allow_guest=True)
def list_company_groups(comp):
	valid_auth_code()
	return frappe.get_all("Cloud Company Group", filters={"company": comp},
						fields=["name", "group_name", "enabled", "description", "creation", "modified"])


@frappe.whitelist(allow_guest=True)
def list_user_groups(user):
	valid_auth_code()
	groups = _list_user_groups(user)
	for g in groups:
		g.group_name = frappe.get_value("Cloud Company Group", g.name, "group_name")
	return groups


@frappe.whitelist(allow_guest=True)
def list_roles():
	valid_auth_code()
	return [d.name for d in frappe.get_all("Cloud User Role")]


@frappe.whitelist(allow_guest=True)
def list_role_permissions(role):
	valid_auth_code()
	return [ d.perm for d in frappe.get_all("Cloud User RolePermission", filters={"parent": role}, fields=["perm"])]


@frappe.whitelist(allow_guest=True)
def login(user=None, passwd=None):
	"""
	HDB Application checking for user login
	:param user: Username (Frappe Username)
	:param pwd: Password (Frappe User Password)
	:return: {"user": <Frappe Username>}
	"""
	valid_auth_code()
	if not (user and passwd):
		user, passwd = frappe.form_dict.get('user'), frappe.form_dict.get('passwd')
	frappe.logger(__name__).debug(_("HDB Checking login user {0} password {1}").format(user, passwd))

	frappe.local.login_manager.authenticate(user, passwd)
	if frappe.local.login_manager.user != user:
		throw(_("Username password is not matched!"))

	companies = list_user_companies(user)

	return {"user": user, "companies": companies}


def list_iot_devices(user):
	frappe.logger(__name__).debug(_("List Devices for user {0}").format(user))

	# Get Enteprise Devices
	ent_devices = []
	groups = _list_user_groups(user)
	companies = list_user_companies(user)
	for g in groups:
		sn_list = [d[0] for d in frappe.db.get_values("IOT Device", {
			"owner_id": g.name,
			"owner_type": "Cloud Company Group"
		}, "sn")]

		ent_devices.append({"group": g.name, "devices": sn_list, "role": g.role})

	# Get Shared Devices
	shd_devices = []
	for shared_group in [ d[0] for d in frappe.db.get_values("IOT ShareGroupUser", {"user": user}, "parent")]:
		# Make sure we will not having shared device from your company
		if frappe.get_value("IOT Share Group", shared_group, "company") in companies:
			continue
		role = frappe.get_value("IOT Share Group", shared_group, "role")

		dev_list = []
		for dev in [d[0] for d in frappe.db.get_values("IOT ShareGroupDevice", {"parent": shared_group}, "device")]:
			dev_list.append(dev)
		shd_devices.append({"group": shared_group, "devices": dev_list, "role": role})

	# Get Private Devices
	pri_devices = [d[0] for d in frappe.db.get_values("IOT Device", {"owner_id": user, "owner_type": "User"}, "sn")]

	devices = {
		"company_devices": ent_devices,
		"private_devices": pri_devices,
		"shared_devices": shd_devices,
	}
	return devices


@frappe.whitelist(allow_guest=True)
def list_devices(user=None):
	"""
	List devices according to user specified in query params by naming as 'usr'
		this user is ERPNext user which you got from @iot.auth.login
	:param user: ERPNext username
	:return: device list
	"""
	valid_auth_code()
	user = user or frappe.form_dict.get('user')
	if not user:
		throw(_("Query string user does not specified"))

	return list_iot_devices(user)


def get_post_json_data():
	if frappe.request.method != "POST":
		throw(_("Request Method Must be POST!"))
	ctype = frappe.get_request_header("Content-Type")
	if "json" not in ctype.lower():
		throw(_("Incorrect HTTP Content-Type found {0}").format(ctype))
	if not frappe.form_dict.data:
		throw(_("JSON Data not found!"))
	return json.loads(frappe.form_dict.data)


@frappe.whitelist(allow_guest=True)
def get_device(sn=None):
	valid_auth_code()
	sn = sn or frappe.form_dict.get('sn')
	if not sn:
		throw(_("Request fields not found. fields: sn"))

	dev = IOTDevice.get_device_doc(sn)
	return __generate_hdb(dev)


@frappe.whitelist(allow_guest=True)
def get_device_db(sn=None):
	valid_auth_code()
	sn = sn or frappe.form_dict.get('sn')
	if not sn:
		throw(_("Request fields not found. fields: sn"))
	company = frappe.get_value("IOT Device", sn, "company")
	return frappe.get_value("Cloud Company", company, "domain")


def fire_callback(cb_url, cb_data):
	frappe.logger(__name__).debug("HDB Fire Callback with data:")
	frappe.logger(__name__).debug(cb_data)
	session = requests.session()
	r = session.post(cb_url, json=cb_data)

	if r.status_code != 200:
		frappe.logger(__name__).error(r.text)
	else:
		frappe.logger(__name__).debug(r.text)


def __generate_hdb(dev):
	if dev.hdb is None or len(dev.hdb) == 0:
		dev.hdb = dev.sn

	# hdb = dev.hdb.replace("-", "").replace("_", "")
	domain = frappe.get_value("Cloud Company", dev.company, "domain")
	dev.hdb = ("/{0}/{1}").format(domain, dev.hdb)
	return dev


def on_device_owner_update(device, org_owner_type=None, org_owner=None):
	url = None #IOTHDBSettings.get_redis_url() // TODO: FixMe
	print(device.sn, device.owner_id)
	if url:
		""" Fire callback data """
		cb_data = {
			'cmd': 'add_device',
			'sn': device.sn,
		}
		if org_owner is not None:
			cb_data['cmd'] = 'update_device'
			cb_data['add_users'] = IOTDevice.find_owners(device.owner_type, device.owner_id)
			cb_data['del_users'] = IOTDevice.find_owners(org_owner_type, org_owner)
		else:
			cb_data['users'] = IOTDevice.find_owners(device.owner_type, device.owner_id)
		print('------------------------------------------')
		print(json.dumps(cb_data))
		print('------------------------------------------')


@frappe.whitelist(allow_guest=True)
def add_device(device_data=None):
	valid_auth_code()
	device = device_data or get_post_json_data()

	sn = device.get("sn")
	if not sn:
		throw(_("Request fields not found. fields: sn"))

	if IOTDevice.check_sn_exists(sn):
		return IOTDevice.get_device_doc(sn)

	device.update({
		"doctype": "IOT Device"
	})

	if not device.get("dev_name"):
		device.update({
			"dev_name": sn
		})

	dev = frappe.get_doc(device).insert()

	# frappe.enqueue('iot.hdb_api.on_device_owner_update', device = dev)

	return __generate_hdb(dev)


@frappe.whitelist(allow_guest=True)
def update_device():
	valid_auth_code()
	data = get_post_json_data()
	dev = add_device(device_data=data)
	if dev.dev_name != data.get("dev_name"):
		dev.update_dev_name(data.get("dev_name"))
	if dev.description != data.get("description"):
		dev.update_dev_description(data.get("description"))
	update_device_owner(device_data=data)
	return update_device_status(device_data=data)


@frappe.whitelist(allow_guest=True)
def update_device_owner(device_data=None):
	valid_auth_code()
	data = device_data or get_post_json_data()
	owner_id = data.get("owner_id")
	owner_type = data.get("owner_type")
	sn = data.get("sn")
	if sn is None:
		throw(_("Request fields not found. fields: sn"))

	dev = IOTDevice.get_device_doc(sn)
	if not dev:
		throw(_("Device is not found. SN:{0}").format(sn))

	if owner_id == "":
		owner_id = None
	if dev.owner_id == owner_id:
		return __generate_hdb(dev)

	org_owner = dev.owner_id
	org_owner_type = dev.owner_type
	dev.update_owner(owner_type, owner_id)

	# frappe.enqueue('iot.hdb_api.on_device_owner_update', device=dev, org_owner_type=org_owner_type, org_owner=org_owner)

	return __generate_hdb(dev)


@frappe.whitelist(allow_guest=True)
def update_device_hdb(device_data=None):
	valid_auth_code()
	data = device_data or get_post_json_data()
	hdb = data.get("hdb")
	sn = data.get("sn")
	if not (sn and hdb):
		throw(_("Request fields not found. fields: sn\thdb"))

	dev = IOTDevice.get_device_doc(sn)
	if not dev:
		throw(_("Device is not found. SN:{0}").format(sn))

	if dev.hdb != hdb:
		dev.update_hdb(hdb)
	return __generate_hdb(dev)


@frappe.whitelist(allow_guest=True)
def update_device_status(device_data=None):
	valid_auth_code()
	data = device_data or get_post_json_data()
	status = data.get("status")
	sn = data.get("sn")
	if not (sn and status):
		throw(_("Request fields not found. fields: sn\tstatus"))

	dev = IOTDevice.get_device_doc(sn)
	if not dev:
		throw(_("Device is not found. SN:{0}").format(sn))

	dev.update_status(status)
	return __generate_hdb(dev)


@frappe.whitelist(allow_guest=True)
def update_device_name():
	valid_auth_code()
	data = get_post_json_data()
	name = data.get("name")
	sn = data.get("sn")
	if not (sn and name):
		throw(_("Request fields not found. fields: sn\tname"))

	dev = IOTDevice.get_device_doc(sn)
	if not dev:
		throw(_("Device is not found. SN:{0}").format(sn))

	dev.update_dev_name(name)
	return __generate_hdb(dev)


@frappe.whitelist(allow_guest=True)
def update_device_position():
	valid_auth_code()
	data = get_post_json_data()
	pos = data.get("position")
	if not isinstance(pos, basestring):
		pos = json.loads(pos)

	sn = data.get("sn")
	if not (sn and pos):
		throw(_("Request fields not found. fields: sn\tposition"))

	dev = IOTDevice.get_device_doc(sn)
	if not dev:
		throw(_("Device is not found. SN:{0}").format(sn))

	dev.update_dev_pos(pos.get("long"), pos.get("lati"))
	return __generate_hdb(dev)


@frappe.whitelist(allow_guest=True)
def add_device_error(err_data=None):
	"""
	Add device error
	:param err_data: {"device": device_sn, "error_type": Error Type defined, "error_key": any text, "error_level": int, "error_info": any text}
	:return: iot_device_error
	"""
	valid_auth_code()
	err_data = err_data or get_post_json_data()
	device = err_data.get("device")
	if not device:
		throw(_("Request fields not found. fields: device"))

	if not IOTDevice.check_sn_exists(device):
		throw(_("Device {0} not found.").format(device))

	err_data.update({
		"doctype": "IOT Device Error"
	})
	doc = frappe.get_doc(err_data).insert().as_dict()

	return doc


@frappe.whitelist(allow_guest=True)
def get_user_session(user):
	valid_auth_code()
	if user:
		frappe.session.get_session_record()


@frappe.whitelist(allow_guest=True)
def get_license_data(sn=None):
	valid_auth_code()
	return frappe.get_value("IOT License", {"name": sn, "enabled": 1}, "license_data")


@frappe.whitelist(allow_guest=True)
def get_time():
	valid_auth_code()
	return frappe.utils.now()


@frappe.whitelist(allow_guest=True)
def ping():
	form_data = frappe.form_dict
	if frappe.request and frappe.request.method == "POST":
		if form_data.data:
			form_data = json.loads(form_data.data)
		return form_data.get("text") or "No Text"
	return 'pong'
