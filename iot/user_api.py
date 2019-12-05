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
from six import string_types
from frappe.utils import convert_utc_to_user_timezone, get_fullname
from frappe import throw, _dict, _
from iot.iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings
from iot.iot.doctype.iot_device.iot_device import IOTDevice
from cloud.cloud.doctype.cloud_company.cloud_company import list_user_companies
from app_center.api import get_latest_version
from iot.device_api import get_post_json_data
from iot.hdb import iot_device_cfg, iot_device_data, iot_device_tree, iot_device_data_array, iot_device_his_data


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
	from iot.hdb_api import list_iot_devices
	return list_iot_devices(frappe.session.user)


@frappe.whitelist(allow_guest=True)
def access_device(sn, op="read"):
	valid_auth_code()
	from iot.hdb_api import access_device as hdb_api_access_device
	return hdb_api_access_device(sn, op)


@frappe.whitelist(allow_guest=True)
def get_device(sn=None):
	valid_auth_code()
	from iot.hdb_api import get_device as hdb_api_get_device
	return hdb_api_get_device(sn)


@frappe.whitelist(allow_guest=True)
def device_tree(sn=None):
	valid_auth_code()
	return iot_device_tree(sn)


@frappe.whitelist(allow_guest=True)
def device_cfg(sn=None, vsn=None):
	valid_auth_code()
	return iot_device_cfg(sn, vsn)


@frappe.whitelist(allow_guest=True)
def device_data(sn=None, vsn=None):
	valid_auth_code()
	return iot_device_data(sn, vsn)


@frappe.whitelist(allow_guest=True)
def device_data_array(sn=None, vsn=None):
	valid_auth_code()
	return iot_device_data_array(sn, vsn)


@frappe.whitelist(allow_guest=True)
def device_history_data(sn=None, vsn=None, fields="*", condition=None):
	valid_auth_code()
	return iot_device_his_data(sn, vsn, fields, condition)


@frappe.whitelist(allow_guest=True)
def device_is_beta(sn):
	valid_auth_code()
	iot_beta_flag = 0
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/12", decode_responses=True)
	try:
		betainfo = client.hget(sn, 'enable_beta/value')
	except Exception as ex:
		return None
	if betainfo:
		iot_beta_flag = eval(betainfo)[1]
	return iot_beta_flag


@frappe.whitelist(allow_guest=True)
def device_enable_beta(sn):
	valid_auth_code()
	doc = frappe.get_doc("IOT Device", sn)
	doc.set_use_beta()
	from iot.device_api import send_action
	return send_action("sys", action="enable/beta", device=sn, data="1")


@frappe.whitelist()
def new_virtual_gate():
	if frappe.request.method != "POST":
		throw(_("Request Method Must be POST!"))
	valid_auth_code()
	doc = frappe.get_doc({
		"doctype": "IOT Virtual Device",
		"user": frappe.session.user,
		"sn": str(uuid.uuid1()).upper(),
	}).insert()
	return doc.name


@frappe.whitelist(allow_guest=True)
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

@frappe.whitelist(allow_guest=True)
def remove_device():
	valid_auth_code()
	postdata = get_post_json_data()
	sn = postdata['sn']
	for s in sn:
		doc = frappe.get_doc("IOT Device", s)
		doc.update_owner("", None)
	return True


@frappe.whitelist(allow_guest=True)
def update_device(sn, name, desc):
	valid_auth_code()
	doc = frappe.get_doc("IOT Device", sn)
	doc.update({
		"dev_name": name,
		"description": desc
	})
	doc.save()
	return True


@frappe.whitelist(allow_guest=True)
def device_public_info(sn):
	valid_auth_code()
	info = {}
	try:
		s = requests.Session()
		s.auth = ("api", "Pa88word")
		r = s.get('http://127.0.0.1:18083/api/v2/nodes/emq@127.0.0.1/clients/' + sn)
		rdict = json.loads(r.text)
		if rdict and rdict['result']:
			objects = rdict['result']['objects']
			if (len(objects) > 0):
				info['public_ip'] = rdict['result']['objects'][0]['ipaddress']
				info['public_port'] = rdict['result']['objects'][0]['port']
	except Exception as ex:
		frappe.logger(__name__).error(ex)

	return info


@frappe.whitelist(allow_guest=True)
def device_info(sn):
	valid_auth_code()
	device = frappe.get_doc('IOT Device', sn)
	if not device.has_permission("read"):
		raise frappe.PermissionError

	device = {
		'sn': device.sn,
		'name': device.dev_name,
		'desc': device.description,
		'company': device.company,
		'location': 'UNKNOWN',  # TODO: Get device location
		'beta': device.use_beta,
		'is_beta': device_is_beta(sn),
		'status': device.device_status,
	}

	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/12", decode_responses=True)
	if client.exists(sn):
		info = client.hgetall(sn)
		if info:
			device['version'] = info.get("version/value")
			device['skynet_version'] = info.get("skynet_version/value")
			_starttime = info.get("starttime/value")
			device['start_time'] = str(
				convert_utc_to_user_timezone(datetime.datetime.utcfromtimestamp(int(_starttime))).replace(
					tzinfo=None))
			device['uptime'] = int(info.get("uptime/value") / 1000)  # convert to seconds
			device['platform'] = info.get("platform/value")

	return device


@frappe.whitelist(allow_guest=True)
def device_app_list(sn):
	from app_center.app_center.doctype.iot_application_version.iot_application_version import IOTApplicationVersion

	valid_auth_code()
	device = frappe.get_doc('IOT Device', sn)
	if not device.has_permission("read"):
		raise frappe.PermissionError

	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/6", decode_responses=True)
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
						"code_name": doc.code_name,
						"app_path": doc.app_path,
						"developer": doc.developer,
						"developer_fullname": get_fullname(doc.developer),
						"version": get_latest_version(doc.name, device.use_beta),
						"fork_from": doc.fork_from,
						"fork_version": doc.fork_version,
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


@frappe.whitelist(allow_guest=True)
def device_app_dev_tree(sn):
	valid_auth_code()
	device_tree = iot_device_tree(sn)
	app_dev_tree = _dict({})

	for dev_sn in device_tree:
		cfg = iot_device_cfg(sn, dev_sn)
		dev_meta = cfg['meta']
		if not dev_meta:
			continue

		app = dev_meta['app']
		if not app:
			continue

		dev_meta['sn']=dev_sn
		if not app_dev_tree.get(app):
			app_dev_tree[app] = []
		app_dev_tree[app].append(dev_meta)

	return app_dev_tree


@frappe.whitelist(allow_guest=True)
def create_batch_task():
	valid_auth_code()
	post_data = get_post_json_data()
	name = post_data.get('name')
	if not isinstance(name, string_types):
		throw(_("Name must be string type!"))
	script = post_data.get('script')
	if not isinstance(script, string_types):
		throw(_("Script must be string type!"))
	devices = post_data.get('devices')
	if not isinstance(devices, list):
		throw(_("Devices not be a list!"))

	doc = frappe.get_doc({
		"doctype": "IOT Batch Task",
		"task_name": name,
		"task_description": post_data.get('description'),
		"batch_script": script,
		"timeout": post_data.get('timeout'),
		"owner_id": frappe.session.user,
	})
	for dev in devices:
		doc.append("device_list", { "device": dev })
	doc = doc.insert()
	frappe.db.commit() # Commit to database to make sure batch task has been there before submit()
	doc.submit()
	return doc.name


@frappe.whitelist(allow_guest=True)
def batch_task_detail(name):
	valid_auth_code()
	return frappe.get_doc("IOT Batch Task", name).as_dict()


@frappe.whitelist(allow_guest=True)
def batch_task_status(name, update=False):
	valid_auth_code()
	if update is not False:
		doc = frappe.get_doc("IOT Batch Task", name)
		doc.update_status()
	return frappe.get_value("IOT Batch Task", name, "status")


@frappe.whitelist(allow_guest=True)
def device_activity_detail(name):
	valid_auth_code()
	return frappe.get_doc("IOT Device Activity", name)


@frappe.whitelist(allow_guest=True)
def dispose_device_activity(name, disposed=1):
	valid_auth_code()
	doc = frappe.get_doc("IOT Device Activity", name)
	doc.dispose(disposed)
	return name


@frappe.whitelist(allow_guest=True)
def dispose_device_activities():
	valid_auth_code()
	post_data = get_post_json_data()
	activities = post_data.get('activities') or []
	disposed = post_data.get('disposed') or 1
	for activity in activities:
		doc = frappe.get_doc("IOT Device Activity", activity)
		doc.dispose(disposed)
	return True


'''
filters = [["creation", ">", "2014-01-01"]]

filters = {"creation": [">", "2014-01-01"], "operation": "Owner"}
'''


@frappe.whitelist(allow_guest=True)
def device_activity(sn=None, start=0, limit=40, filters=None):
	from iot.iot.doctype.iot_device_activity.iot_device_activity import query_logs_by_user as _query_logs_by_user
	from iot.iot.doctype.iot_device_activity.iot_device_activity import query_logs_by_device as _query_logs_by_device
	valid_auth_code()
	if sn:
		return _query_logs_by_device(sn, start, limit, filters)
	else:
		return _query_logs_by_user(frappe.session.user, start, limit, filters)


@frappe.whitelist(allow_guest=True)
def count_device_activity(sn=None, filters=None):
	from iot.iot.doctype.iot_device_activity.iot_device_activity import count_logs_by_user as _count_logs_by_user
	from iot.iot.doctype.iot_device_activity.iot_device_activity import count_logs_by_device as _count_logs_by_device
	valid_auth_code()
	if sn:
		return _count_logs_by_device(sn, filters)
	else:
		return _count_logs_by_user(frappe.session.user, filters)


@frappe.whitelist(allow_guest=True)
def device_activity_by_company(company, start=0, limit=40, filters=None):
	from iot.iot.doctype.iot_device_activity.iot_device_activity import query_logs_by_company as _query_logs_by_company
	valid_auth_code()
	if frappe.get_value("Cloud Employee", frappe.session.user, "company") != company:
		return None
	return _query_logs_by_company(company, start, limit, filters)


@frappe.whitelist(allow_guest=True)
def count_device_activity_by_company(company, filters):
	from iot.iot.doctype.iot_device_activity.iot_device_activity import count_logs_by_company as _count_logs_by_company
	valid_auth_code()
	if frappe.get_value("Cloud Employee", frappe.session.user, "company") != company:
		return None
	return _count_logs_by_company(company, filters)


@frappe.whitelist(allow_guest=True)
def device_event_detail(name):
	valid_auth_code()
	return frappe.get_doc("IOT Device Event", name)


@frappe.whitelist(allow_guest=True)
def dispose_device_event(name, disposed=1):
	valid_auth_code()
	doc = frappe.get_doc("IOT Device Event", name)
	doc.dispose(disposed)
	return name


@frappe.whitelist(allow_guest=True)
def dispose_device_events():
	valid_auth_code()
	post_data = get_post_json_data()
	events = post_data.get('events') or []
	disposed = post_data.get('disposed') or 1
	for event in events:
		doc = frappe.get_doc("IOT Device Event", event)
		doc.dispose(disposed)
	return True


'''
filters = [["creation", ">", "2014-01-01"]]

filters = {"creation": [">", "2014-01-01"], "event_type": "系统"}
filters = {"creation": [">", "2014-01-01"], "event_type": "系统", "event_level": 1}
'''


@frappe.whitelist(allow_guest=True)
def device_event(sn=None, start=0, limit=40, filters=None):
	from iot.iot.doctype.iot_device_event.iot_device_event import query_device_event as _query_device_event
	valid_auth_code()
	return _query_device_event(sn, start, limit, filters)


@frappe.whitelist(allow_guest=True)
def count_device_event(sn=None, filters=None):
	from iot.iot.doctype.iot_device_event.iot_device_event import count_device_event as _count_device_event
	valid_auth_code()
	return _count_device_event(sn, filters)


@frappe.whitelist(allow_guest=True)
def device_event_by_company(company, start=0, limit=40, filters=None):
	from iot.iot.doctype.iot_device_event.iot_device_event import query_device_event_by_company as _query_device_event_by_company
	valid_auth_code()
	if frappe.get_value("Cloud Employee", frappe.session.user, "company") != company:
		return None
	return _query_device_event_by_company(company, start, limit, filters)


@frappe.whitelist(allow_guest=True)
def count_device_event_by_company(company, filters=None):
	from iot.iot.doctype.iot_device_event.iot_device_event import count_device_event_by_company as _count_device_event_by_company
	valid_auth_code()
	if frappe.get_value("Cloud Employee", frappe.session.user, "company") != company:
		return None
	return _count_device_event_by_company(company, filters)


@frappe.whitelist(allow_guest=True)
def firmware_last_version_by_platform(platform, beta=0):
	valid_auth_code()
	return {
		"skynet": get_latest_version(platform + "_skynet", int(beta)),
		"freeioe": get_latest_version("freeioe", int(beta))
	}


@frappe.whitelist(allow_guest=True)
def firmware_last_version(sn, beta=0):
	valid_auth_code()
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/12", decode_responses=True)
	if client.exists(sn):
		info = client.hgetall(sn)
		if info:
			platform = info.get("platform/value")
			if platform:
				return firmware_last_version_by_platform(platform, beta)

	return None


UTC_FORMAT1 = "%Y-%m-%dT%H:%M:%S.%fZ"
UTC_FORMAT2 = "%Y-%m-%dT%H:%M:%SZ"


@frappe.whitelist(allow_guest=True)
def device_status_statistics():
	valid_auth_code()
	companies = list_user_companies(frappe.session.user)
	if len(companies) == 0:
		return
	company = companies[0]

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


@frappe.whitelist(allow_guest=True)
def device_event_type_statistics():
	valid_auth_code()
	companies = list_user_companies(frappe.session.user)
	if len(companies) == 0:
		return
	company = companies[0]

	inf_server = IOTHDBSettings.get_influxdb_server()
	if not inf_server:
		frappe.logger(__name__).error("InfluxDB Configuration missing in IOTHDBSettings")
		return

	query = 'SELECT sum("SYS"), sum("DEV"), sum("COMM"), sum("DATA"), sum("APP")'
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


@frappe.whitelist(allow_guest=True)
def device_event_count_statistics():
	valid_auth_code()
	companies = list_user_companies(frappe.session.user)
	if len(companies) == 0:
		return
	company = companies[0]

	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/15", decode_responses=True)

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


@frappe.whitelist(allow_guest=True)
def device_type_statistics():
	valid_auth_code()
	companies = list_user_companies(frappe.session.user)
	if len(companies) == 0:
		return
	company = companies[0]

	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/15", decode_responses=True)
	try:
		return client.hgetall('device_type.' + company)
	except Exception as ex:
		return []


@frappe.whitelist(allow_guest=True)
def list_statistics_companies():
	'''
	Cloud statistics enabled when company owner has created its user auth code
	:return:
	'''
	valid_auth_code()

	if 'IOT Manager' not in frappe.get_roles():
		return []

	list = []
	companies = frappe.get_all("Cloud Company", fields=["name", "admin", "domain", "enabled"])
	for comp in companies:
		auth_code = frappe.get_value("IOT User Api", comp.admin, "authorization_code")
		if auth_code and comp.enabled == 1:
			list.append({
				'company': comp.name,
				'auth_code': auth_code,
				'database': comp.domain,
				'enable': 1,
			})
		else:
			list.append({
				'company': comp.name,
				'auth_code': 'UNKNOWN',
				'database': comp.domain,
				'enable': 0,
			})

	return list


@frappe.whitelist(allow_guest=True)
def list_user_apps(user=None):
	valid_auth_code()

	if 'IOT Manager' not in frappe.get_roles():
		return []

	from iot.iot_hub.doctype.iot_user_application.iot_user_application import list_user_apps as _list_user_apps
	return _list_user_apps(user)


@frappe.whitelist(allow_guest=True)
def ping():
	return 'pong from iot.user_api.ping'
