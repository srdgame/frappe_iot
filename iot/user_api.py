# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt
#
# RESTFul API for IOT User which has his/her auth code
#

from __future__ import unicode_literals
import frappe
import json
import redis
import datetime
import uuid
import requests
import hdb_api
import hdb
from frappe.utils import now, get_datetime, convert_utc_to_user_timezone, get_fullname
from frappe import throw, msgprint, _, _dict
from iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings
from iot.doctype.iot_device.iot_device import IOTDevice
from app_center.api import get_latest_version
from cloud.cloud.doctype.cloud_company.cloud_company import list_user_companies, list_users, get_domain
from device_api import get_post_json_data


def valid_auth_code(auth_code=None):
	if 'Guest' != frappe.session.user:
		return
	auth_code = auth_code or frappe.get_request_header("AuthorizationCode")
	if not auth_code:
		throw(_("AuthorizationCode is required in HTTP Header!"))
	frappe.logger(__name__).debug(_("API AuthorizationCode as {0}").format(auth_code))

	user = frappe.get_value("IOT User Api", {"authorization_code": auth_code}, "user")
	if not user:
		throw(_("Authorization Code is incorrect!"))

	# form dict keeping
	form_dict = frappe.local.form_dict
	frappe.set_user(user)
	frappe.local.form_dict = form_dict


@frappe.whitelist(allow_guest=True)
def get_user():
	valid_auth_code()
	return frappe.session.user


@frappe.whitelist(allow_guest=True)
def gen_uuid():
	return str(uuid.uuid1()).upper()


@frappe.whitelist(allow_guest=True)
def list_devices():
	valid_auth_code()
	return hdb_api.list_iot_devices(frappe.session.user)


@frappe.whitelist(allow_guest=True)
def get_device(sn=None):
	valid_auth_code()
	return hdb_api.get_device(sn)


@frappe.whitelist(allow_guest=True)
def device_tree(sn=None):
	valid_auth_code()
	return hdb.iot_device_tree(sn)


@frappe.whitelist(allow_guest=True)
def device_cfg(sn=None, vsn=None):
	valid_auth_code()
	return hdb.iot_device_cfg(sn, vsn)


@frappe.whitelist(allow_guest=True)
def device_data(sn=None, vsn=None):
	valid_auth_code()
	return hdb.iot_device_data(sn, vsn)


@frappe.whitelist(allow_guest=True)
def device_data_array(sn=None, vsn=None):
	valid_auth_code()
	return hdb.iot_device_data_array(sn, vsn)


@frappe.whitelist(allow_guest=True)
def device_history_data(sn=None, vsn=None, fields="*", condition=None):
	valid_auth_code()
	return hdb.iot_device_his_data(sn, vsn, fields, condition)


@frappe.whitelist()
def device_is_beta(sn):
	iot_beta_flag = 0
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/12")
	try:
		betainfo = client.hget(sn, 'enable_beta/value')
	except Exception as ex:
		return None
	if betainfo:
		iot_beta_flag = eval(betainfo)[1]
	return iot_beta_flag


@frappe.whitelist()
def device_enable_beta(sn):
	valid_auth_code()
	doc = frappe.get_doc("IOT Device", sn)
	doc.set_use_beta()
	from iot.device_api import send_action
	return send_action("sys", action="enable/beta", device=sn, data="1")


@frappe.whitelist()
def add_device(sn, name, desc, owner_type):
	valid_auth_code()
	type = "User"
	owner = frappe.session.user
	if owner_type == 2:
		company = list_user_companies(frappe.session.user)[0]
		try:
			owner = frappe.get_value("Cloud Company Group", {"company": company, "group_name": "root"})
			type = "Cloud Company Group"
		except Exception as ex:
			throw(_("Cannot find default group in company{0}. Error: {1}").format(company, repr(ex)))

	iot_device = None
	sn_exists = frappe.db.get_value("IOT Device", {"sn": sn}, "sn")
	if not sn_exists:
		iot_device = frappe.get_doc({"doctype": "IOT Device", "sn": sn, "dev_name": name, "description": desc, "owner_type": type, "owner_id": owner})
		iot_device.insert(ignore_permissions=True)
	else:
		iot_device = frappe.get_doc("IOT Device", sn)

	if iot_device.owner_id:
		if iot_device.owner_id == owner and iot_device.owner_type == type:
			return True
		throw(_("Device {0} is owned by {1}").format(sn, iot_device.owner_id))
	else:
		iot_device.set("dev_name", name)
		iot_device.set("description", desc)
		iot_device.update_owner(type, owner)
		return True

@frappe.whitelist()
def remove_device():
	valid_auth_code()
	postdata = get_post_json_data()
	sn = postdata['sn']
	for s in sn:
		doc = frappe.get_doc("IOT Device", s)
		doc.update_owner("", None)
	return True


@frappe.whitelist()
def update_device(sn, name, desc):
	valid_auth_code()
	doc = frappe.get_doc("IOT Device", sn)
	doc.update({
		"dev_name": name,
		"description": desc
	})
	doc.save()
	return True


@frappe.whitelist()
def device_info(sn):
	valid_auth_code()
	device = frappe.get_doc('IOT Device', sn)
	if not device.has_permission("read"):
		raise frappe.PermissionError
	basic = {
		'sn': device.sn,
		'model': "Q102",
		'name': device.dev_name,
		'desc': device.description,
		'company': device.company,
		'location': device.sn,
		'beta': device.use_beta,
		'iot_beta': device_is_beta(sn),
		'status': device.device_status,
	}
	config = {}
	applist = {}
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/12")
	if client.exists(sn):
		info = client.hgetall(sn)
		if info:
			config['iot_version'] = eval(info.get("version/value"))[1]
			config['skynet_version'] = eval(info.get("skynet_version/value"))[1]
			_starttime = eval(info.get("starttime/value"))[1]
			config['starttime'] = str(
				convert_utc_to_user_timezone(datetime.datetime.utcfromtimestamp(int(_starttime))).replace(
					tzinfo=None))
			config['uptime'] = int(eval(info.get("uptime/value"))[1] / 1000)
			print(info.get("skynet_platform/value"))
			config['platform'] = eval(info.get("platform/value"))[1]

		try:
			s = requests.Session()
			s.auth = ("api", "Pa88word")
			r = s.get('http://127.0.0.1:18083/api/v2/nodes/emq@127.0.0.1/clients/' + sn)
			rdict = json.loads(r.text)
			if rdict and rdict['result']:
				objects = rdict['result']['objects']
				if (len(objects) > 0):
					config['public_ip'] = rdict['result']['objects'][0]['ipaddress']
					config['public_port'] = rdict['result']['objects'][0]['port']
		except Exception as ex:
			frappe.logger(__name__).error(ex)

		config['cpu'] = "imx6ull 528MHz"
		config['ram'] = "256 MB"
		config['rom'] = "4 GB"
		config['os'] = "openwrt"
	try:
		client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/6")
		applist = json.loads(client.get(sn))
	except Exception as ex:
		applist = {}

	return {
		'basic': basic,
		'config': config,
		'applist': applist,
	}


@frappe.whitelist()
def device_app_list(sn):
	from app_center.app_center.doctype.iot_application_version.iot_application_version import IOTApplicationVersion

	valid_auth_code()
	device = frappe.get_doc('IOT Device', sn)
	if not device.has_permission("read"):
		raise frappe.PermissionError

	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/6")
	applist = json.loads(client.get(sn) or "[]")

	iot_applist = []
	for app in applist:
		app_obj = _dict(applist[app])
		try:
			applist[app]['inst'] = app

			if not frappe.get_value("IOT Application", app_obj.name, "name"):
				iot_applist.append({
					"cloud": None,
					"info": applist[app],
					"inst": app,
				})
				continue
			else:
				doc = frappe.get_doc("IOT Application", app_obj.name)
				if app_obj.auto is None:
					applist[app]['auto'] = "1"

				iot_applist.append({
					"cloud": {
						"name": doc.name,
						"app_name": doc.app_name,
						"owner": doc.owner,
						"fullname": get_fullname(doc.owner),
						"ver": IOTApplicationVersion.get_latest_version(doc.name),
						"fork_app": doc.fork_from,
						"fork_ver": doc.fork_version,
						"icon_image": doc.icon_image,
					},
					"info": applist[app],
					"inst": app,
				})

		except Exception as ex:
			frappe.logger(__name__).error(ex)
			iot_applist.append({
				"cloud": None,
				"info": applist[app],
				"inst": app,
			})

	return iot_applist


@frappe.whitelist()
def device_app_dev_tree(sn):
	from iot.hdb import iot_device_tree as _iot_device_tree
	from iot.hdb import iot_device_cfg as _iot_device_cfg

	valid_auth_code()
	device_tree = _iot_device_tree(sn)
	app_dev_tree = _dict({})

	for devsn in device_tree:
		cfg = _iot_device_cfg(sn, devsn)
		devmeta = cfg['meta']
		if not devmeta:
			continue

		app = devmeta['app']
		if not app:
			continue

		devmeta['sn']=devsn
		if not app_dev_tree.get(app):
			app_dev_tree[app] = []
		app_dev_tree[app].append(devmeta)

	return app_dev_tree


UTC_FORMAT1 = "%Y-%m-%dT%H:%M:%S.%fZ"
UTC_FORMAT2 = "%Y-%m-%dT%H:%M:%SZ"


@frappe.whitelist()
def store_app_list(category=None, protocol=None, device_supplier=None, user=None, name=None, app_name=None):
	valid_auth_code()
	filters = {"owner": ["!=", "Administrator"]}
	if user:
		filters = {"owner": user}
	if category:
		filters["category"] = category
	if protocol:
		filters["protocol"] = protocol
	if device_supplier:
		filters["device_supplier"] = device_supplier
	if name:
		filters["name"] = name
	if app_name:
		filters["app_name"] = app_name
	filters["published"] = 1
	filters["license_type"] = 'Open'

	apps = frappe.db.get_all("IOT Application", "*", filters, order_by="modified desc")
	return apps


@frappe.whitelist()
def store_app_category():
	valid_auth_code()
	return frappe.get_all("App Category", fields=["name", "description"])


@frappe.whitelist()
def store_app_supplier():
	valid_auth_code()
	return frappe.get_all("App Device Supplier", fields=["name", "description"])


@frappe.whitelist()
def store_app_protocol():
	valid_auth_code()
	return frappe.get_all("App Device Protocol", fields=["name", "description"])


@frappe.whitelist()
def store_app_detail(app_name):
	valid_auth_code()
	return frappe.get_doc('IOT Application', app_name)


@frappe.whitelist()
def query_device_activity():
	valid_auth_code()
	from iot.doctype.iot_device_activity.iot_device_activity import query_logs_by_user as _query_logs_by_user
	return _query_logs_by_user(frappe.session.user)


@frappe.whitelist()
def query_device_activity_by_company(company):
	valid_auth_code()
	if frappe.get_value("Cloud Employee", frappe.session.user, "company") != company:
		return None

	from iot.doctype.iot_device_activity.iot_device_activity import query_logs_by_company as _query_logs_by_company
	return _query_logs_by_company(company)


@frappe.whitelist()
def query_firmware_lastver(sn, beta):
	valid_auth_code()
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/12")
	if client.exists(sn):
		info = client.hgetall(sn)
		if info:
			device_platform = eval(info.get("platform/value"))[1]
			firmware_lastver = get_latest_version(device_platform+"_skynet", int(beta))
			freeioe_lastver = get_latest_version("freeioe", int(beta))
			return {"firmware_lastver": firmware_lastver, "freeioe_lastver": freeioe_lastver}

	return None


@frappe.whitelist()
def device_status_statistics():
	valid_auth_code()
	company = frappe.get_value('Cloud Employee', frappe.session.user, 'company')
	if not company:
		return

	inf_server = IOTHDBSettings.get_influxdb_server()
	if not inf_server:
		frappe.logger(__name__).error("InfluxDB Configuration missing in IOTHDBSettings")
		return

	query = 'SELECT "online", "offline" FROM "device_status_statistics" WHERE time > now() - 12h AND "owner"=\'' + company + '\''
	domain = frappe.get_value("Cloud Company", company, "domain")
	r = requests.session().get(inf_server + "/query", params={"q": query, "db": domain + '.statistics'}, timeout=10)
	if r.status_code == 200:
		ret = r.json()
		if not ret:
			return

		results = ret['results']
		if not results or len(results) < 1:
			return

		series = results[0].get('series')
		if not series or len(series) < 1:
			return

		res = series[0].get('values')
		if not res:
			return

		taghis = []
		for i in range(0, len(res)):
			hisvalue = {}
			# print('*********', res[i][0])
			try:
				utc_time = datetime.datetime.strptime(res[i][0], UTC_FORMAT1)
			except Exception as err:
				pass
			try:
				utc_time = datetime.datetime.strptime(res[i][0], UTC_FORMAT2)
			except Exception as err:
				pass
			local_time = str(convert_utc_to_user_timezone(utc_time).replace(tzinfo=None))
			hisvalue = {'name': 'device_status_statistics', 'online': res[i][1], 'time': local_time, 'offline': res[i][2], 'owner': company}
			taghis.append(hisvalue)
		return taghis


@frappe.whitelist()
def device_event_type_statistics():
	valid_auth_code()
	company = frappe.get_value('Cloud Employee', frappe.session.user, 'company')
	if not company:
		return

	inf_server = IOTHDBSettings.get_influxdb_server()
	if not inf_server:
		frappe.logger(__name__).error("InfluxDB Configuration missing in IOTHDBSettings")
		return

	query = 'SELECT sum("系统") AS "系统", sum("设备") AS "设备", sum("通讯") AS "通讯", sum("数据") AS "数据", sum("应用") AS "应用"'
	query = query + ' FROM "device_event_type_statistics" WHERE time > now() - 7d'
	query = query + ' AND "owner"=\'' + company + '\' GROUP BY time(1d) FILL(0)'
	domain = frappe.get_value("Cloud Company", company, "domain")
	r = requests.session().get(inf_server + "/query", params={"q": query, "db": domain + '.statistics'}, timeout=10)
	if r.status_code == 200:
		ret = r.json()
		if not ret:
			return

		results = ret['results']
		if not results or len(results) < 1:
			return

		series = results[0].get('series')
		if not series or len(series) < 1:
			return

		res = series[0].get('values')
		if not res:
			return

		taghis = []
		for i in range(0, len(res)):
			hisvalue = {}
			# print('*********', res[i][0])
			try:
				utc_time = datetime.datetime.strptime(res[i][0], UTC_FORMAT1)
			except Exception as err:
				pass
			try:
				utc_time = datetime.datetime.strptime(res[i][0], UTC_FORMAT2)
			except Exception as err:
				pass
			local_time = str(convert_utc_to_user_timezone(utc_time).replace(tzinfo=None))
			hisvalue = {'name': 'device_event_type_statistics', 'time': local_time, 'owner': company}
			hisvalue['系统'] = res[i][1] or 0
			hisvalue['设备'] = res[i][2] or 0
			hisvalue['通讯'] = res[i][3] or 0
			hisvalue['数据'] = res[i][4] or 0
			hisvalue['应用'] = res[i][5] or 0
			taghis.append(hisvalue)
		return taghis


@frappe.whitelist()
def device_event_count_statistics():
	valid_auth_code()
	company = frappe.get_value('Cloud Employee', frappe.session.user, 'company')
	if not company:
		return

	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/15")

	from iot.hdb_api import list_iot_devices as _list_iot_devices
	devices = _list_iot_devices(frappe.session.user)
	company_devices = devices.get('company_devices')

	try:
		result = []
		if company_devices:
			for group in company_devices:
				devices = group["devices"]
				for dev in devices:
					devdoc = IOTDevice.get_device_doc(dev)
					if devdoc:
						vals = client.hgetall('event_count.' + dev)
						vals['sn'] = dev
						vals['name'] = devdoc.dev_name
						vals['last_updated'] = str(devdoc.last_updated)[:-7]
						vals['position'] = 'N/A'
						vals['device_status'] = devdoc.device_status
						result.append(vals)

		return result
	except Exception as ex:
		return []


@frappe.whitelist()
def device_type_statistics():
	valid_auth_code()
	company = frappe.get_value('Cloud Employee', frappe.session.user, 'company')
	if not company:
		return

	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/15")
	try:
		return client.hgetall('device_type.' + company)
	except Exception as ex:
		return []
