# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import throw, msgprint, _
from frappe.model.document import Document
from iot.doctype.iot_device.iot_device import IOTDevice


def valid_auth_code(auth_code=None):
	auth_code = auth_code or frappe.get_request_header("HDB_AuthorizationCode")
	if not auth_code:
		throw(_("HDB_AuthorizationCode is required in your HTTP Header!"))
	frappe.logger(__name__).debug(_("HDB_AuthorizationCode as {0}").format(auth_code))

	code = frappe.db.get_single_value("IOT HDB Settings", "authorization_code")
	if auth_code != code:
		throw(_("Authorization Code is incorrect!"))

	frappe.session.user = frappe.db.get_single_value("IOT HDB Settings", "on_behalf")


@frappe.whitelist(allow_guest=True)
def login(usr=None, pwd=None):
	"""
	HDB Application checking for user login
	:param usr: Username (<Login Name>@<IOT Enterprise Domain>)
	:param pwd: Password (ERPNext User Password)
	:return: {"usr": <ERPNext user name>, "ent": <IOT Enterprise>}
	"""
	valid_auth_code()
	if not (usr and pwd):
		usr, pwd = frappe.form_dict.get('usr'), frappe.form_dict.get('pwd')
	frappe.logger(__name__).debug(_("HDB Checking login {0} password {1}").format(usr, pwd))

	if '@' not in usr:
		throw(_("Username must be <login_name>@<enterprise domain>"))

	login_name, domain = usr.split('@')
	enterprise = frappe.db.get_value("IOT Enterprise", {"domain": domain}, "name")
	if not enterprise:
		throw(_("Enterprise Domain {0} does not exists").format(domain))

	user = frappe.db.get_value("IOT User", {"enterprise": enterprise, "login_name": login_name}, "user")
	if not user:
		throw(_("User login_name {0} not found in Enterprise {1}").format(login_name, enterprise))

	frappe.local.login_manager.authenticate(user, pwd)
	if frappe.local.login_manager.user != user:
		throw(_("Username password is not matched!"))
	
	return {"usr": user, "ent": enterprise}


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
	frappe.logger(__name__).debug(_("List Devices for user {0}").format(user))

	user_doc = frappe.get_doc("IOT User", user)
	groups = user_doc.get("group_assigned")
	print(groups)
	devices = []
	for g in groups:
		bunch_codes = [d[0] for d in frappe.db.get_values("IOT Device Bunch", {"group": g.group}, "code")]
		sn_list = []
		for c in bunch_codes:
			sn_list.append({"bunch": c, "sn": IOTDevice.list_device_sn_by_bunch(c)})
		devices.append({"group": g.group, "devices": sn_list})

	return devices


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
def get_device():
	valid_auth_code()
	data = get_post_json_data()
	sn = data.get("sn")
	if not sn:
		return {"result": False, "data": _("Request fields not found. fields: sn")}

	dev = IOTDevice.get_device_doc(sn)
	return {"result": True, "data": dev}


@frappe.whitelist(allow_guest=True)
def add_device():
	valid_auth_code()
	device = get_post_json_data()
	sn = device.get("sn")
	if not sn:
		return {"result": False, "data": _("Request fields not found. fields: sn")}

	if IOTDevice.check_sn_exists(sn):
		print(IOTDevice.get_device_doc(sn))
		return {"result": True, "data": IOTDevice.get_device_doc(sn)}

	device.update({
		"doctype": "IOT Device"
	})
	data = frappe.get_doc(device).insert().as_dict()
	frappe.db.commit()
	url = frappe.db.get_single_value("IOT HDB Settings", "callback_url")
	r = frappe.session.post(url, data={
		'cmd': 'add_device',
		'sn': sn
		# 'user': password
	})

	if r.status_code != 200:
		frappe.logger(__name__).error(r.json())

	return {"result": True, "data": data}


@frappe.whitelist(allow_guest=True)
def update_device():
	valid_auth_code()
	result = add_device()
	if result["result"]:
		update_device_bench()
		update_device_status()

	return result


@frappe.whitelist(allow_guest=True)
def update_device_bench():
	valid_auth_code()
	data = get_post_json_data()
	bunch = data.get("bunch")
	sn = data.get("sn")
	if not (sn and bunch):
		return {"result": False, "data": _("Request fields not found. fields: sn\tbunch")}

	dev = IOTDevice.get_device_doc(sn)
	if not dev:
		return {"result": False, "data": _("Device is not found. SN:{0}").format(sn)}

	dev.update_bunch(bunch)
	frappe.db.commit()
	return {"result": True, "data": bunch}


@frappe.whitelist(allow_guest=True)
def update_device_status():
	valid_auth_code()
	data = get_post_json_data()
	status = data.get("status")
	sn = data.get("sn")
	if not (sn and status):
		return {"result": False, "data": _("Request fields not found. fields: sn\tstatus")}

	dev = IOTDevice.get_device_doc(sn)
	if not dev:
		return {"result": False, "data": _("Device is not found. SN:{0}").format(sn)}

	dev.update_status(status)
	frappe.db.commit()
	return {"result": True, "info": status}


@frappe.whitelist(allow_guest=True)
def ping():
	form_data = frappe.form_dict
	if frappe.request and frappe.request.method == "POST":
		if form_data.data:
			form_data = json.loads(form_data.data)
		return form_data.get("text") or "No Text"
	return 'pong'


