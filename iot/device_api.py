# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import redis
import uuid
from frappe import throw, msgprint, _
from iot.iot.doctype.iot_device_activity.iot_device_activity import add_device_action_log
from iot.iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings

### TODO: Activity Log


def valid_auth_code():
	if frappe.session.user != "Guest":
		return
	auth_code = frappe.get_request_header("HDB-AuthorizationCode")
	user = None
	if auth_code:
		frappe.logger(__name__).debug(_("HDB-AuthorizationCode as {0}").format(auth_code))

		user = IOTHDBSettings.get_on_behalf(auth_code)
	else:
		auth_code = frappe.get_request_header("AuthorizationCode")
		if auth_code:
			user = frappe.get_value("IOT User Api", {"authorization_code": auth_code}, "user")
		else:
			throw(_("Authorization Code/Login is required!"))

	if not user:
		throw(_("Authorization Code is incorrect!"))

	# form dict keeping
	form_dict = frappe.local.form_dict
	frappe.set_user(user)
	frappe.local.form_dict = form_dict


def get_post_json_data():
	if frappe.request.method != "POST":
		throw(_("Request Method Must be POST!"))
	ctype = frappe.get_request_header("Content-Type")
	if "json" not in ctype.lower():
		throw(_("Incorrect HTTP Content-Type found {0}").format(ctype))
	data = frappe.request.get_data()
	if not data:
		throw(_("JSON Data not found!"))
	return json.loads(data.decode('utf-8'))


@frappe.whitelist(allow_guest=True)
def get_action_result(id):
	'''
	Get action result, result example:
	{
		"message": "Done",
		"timestamp_str": "Wed Aug 29 09:39:08 2018",
		"result": true,
		"timestamp": 1535535548.28,
		"device": "000C296CBED3",
		"id": "605063B4-AB6F-11E8-8C76-00163E06DD4A"
	}
	:return:
	'''
	valid_auth_code()
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/7", decode_responses=True)
	str = client.get(id)
	if str:
		return json.loads(str)


def valid_app_permission(device, data):
	print("Valid Application Permission")
	owner_type = device.owner_type
	owner_id = device.owner_id
	app = data.get("name")
	ret = False
	if owner_type == 'User':
		from app_center.api import user_access
		ret = user_access(app, owner_id)
	else:
		from app_center.api import company_access
		ret = company_access(app, owner_id)

	if not ret:
		throw(_("Not permitted"), frappe.PermissionError)


action_validation = {
	"app": {
		"install": valid_app_permission,
		"upgrade": valid_app_permission
	}
}


@frappe.whitelist(allow_guest=True)
def send_action(channel, action=None, id=None, device=None, data=None):
	valid_auth_code()
	if data is None:
		data = get_post_json_data()
	if id is None:
		id = str(uuid.uuid1()).upper()

	if not device:
		throw(_("Device SN does not exits!"))

	doc = frappe.get_doc("IOT Device", device)
	if not doc.has_permission("write"):
		add_device_action_log(doc, channel, action, id, data, "Failed", "Permission error")
		throw(_("Not permitted"), frappe.PermissionError)

	valids = action_validation.get(channel)
	if valids:
		valid_func = valids.get(action)
		if valid_func:
			valid_func(doc, data)

	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server(), decode_responses=True)
	args = {
		"id": id,
		"device": device,
		"data": data,
	}
	if action:
		args.update({
			"action": action,
		})
	r = client.publish("device_" + channel, json.dumps(args))
	if r <= 0:
		add_device_action_log(doc, channel, action, id, data, "Failed", "Redis error")
		throw(_("Redis message published, but no listener!"))

	add_device_action_log(doc, channel, action, id, data)
	return id


@frappe.whitelist(allow_guest=True)
def app_list():
	data = get_post_json_data()
	return send_action("app", action="list", id=data.get("id"), device=data.get("device"), data="1")


@frappe.whitelist(allow_guest=True)
def app_install():
	data = get_post_json_data()
	return send_action("app", action="install", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def app_uninstall():
	data = get_post_json_data()
	return send_action("app", action="uninstall", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def app_upgrade():
	data = get_post_json_data()
	return send_action("app", action="upgrade", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def app_conf():
	data = get_post_json_data()
	return send_action("app", action="conf", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def app_start():
	'''
	Start application, data example: {"inst": "bms", "conf": "{}"} conf is optional
	:return:
	'''
	data = get_post_json_data()
	return send_action("app", action="start", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def app_stop():
	'''
	Stop application, data example: {"inst": "bms", "reason": "debug stop"}
	:return:
	'''
	data = get_post_json_data()
	return send_action("app", action="stop", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def app_restart():
	'''
	Restart application, data example: {"inst": "bms", "reason": "debug restart"}
	:return:
	'''
	data = get_post_json_data()
	return send_action("app", action="restart", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def app_query_log():
	'''
	Query application log, data example: {"inst": "bms"}
	:return:
	'''
	data = get_post_json_data()
	return send_action("app", action="query_log", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def app_query_comm():
	'''
	Query application communication stream, data example: {"inst": "bms"}
	:return:
	'''
	data = get_post_json_data()
	return send_action("app", action="query_comm", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def app_upload_comm():
	'''
	Upload application communication stream, data example: {"inst": "bms", "sec": 60}
	:return:
	'''
	data = get_post_json_data()
	return send_action("app", action="upload_comm", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def app_option():
	'''
	Set application option value, data example: {"inst": "bms", "option": "auto", "value": 1}
	:return:
	'''
	data = get_post_json_data()
	return send_action("app", action="option", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def app_rename():
	'''
	Rename application instance name, data example: {"inst": "bms", "new_name": "bms2"}
	:return:
	'''
	data = get_post_json_data()
	return send_action("app", action="rename", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_upgrade():
	'''
	Upgrade IOT System, data example: { "no_ack": 1, "version": 601, "skynet": { "version": 1666} }
		"skynet" is optional, and do not set it if you do not want to upgrade skynet
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="upgrade", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_upgrade_ack():
	'''
	IOT System upgrade ack. you need to call this when no_ack is not set in sys_upgrade(), data example: {}
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="upgrade/ack", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_ext_list():
	'''
	List System installed extensions, data example: {}
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="ext/list", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_ext_upgrade():
	'''
	Upgrade IOT System Extension, data example: {"name": "frpc", "version": "latest"}
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="ext/upgrade", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_enable_data():
	'''
	Enable/Disable data upload, enable if data is 1
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="enable/data", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_enable_data_one_short():
	'''
	Enable/Disable data upload for one short, data is the duration for data uploading.
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="enable/data_one_short", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_enable_log():
	'''
	Enable log upload for specified time, data is the how long will log be uploaded
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="enable/log", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_enable_comm():
	'''
	Enable log upload for specified time, data is the how long will log be uploaded
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="enable/comm", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_enable_stat():
	'''
	Enable/Disable data upload, enable if data is 1
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="enable/stat", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_enable_event():
	'''
	Enable/Disable event upload, disable if data is minus number or it is the minimum event level
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="enable/event", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_enable_beta():
	'''
	Enable/Disable data upload, enable if data is 1
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="enable/beta", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_batch_script():
	'''
	Enable/Disable data upload, enable if data is 1
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="batch_script", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_restart():
	'''
	Restart FreeIOE.
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="restart", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_reboot():
	'''
	Reboot device.
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="reboot", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_cloud_conf():
	'''
	Change IOT Device Cloud Settings, data example: {"ID": "IDIDIDIDIDID", "HOST": "ioe.symgrid.com", ...}
		Valid keys: ID/CLOUD_ID/HOST/PORT/TIMEOUT/PKG_HOST_URL/CNF_HOST_URL/DATA_UPLOAD/DATA_UPLOAD_PERIOD/COV/COV_TTL
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="cloud_conf", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_download_cfg():
	'''
	Download IOT Device CFG, data example: {"name": "deab2776ef", "host": "ioe.symgrid.com"}  host is optional
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="cfg/download", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_download_cfg():
	'''
	Upload IOT Device CFG to specified host, data example: {"host": "ioe.symgrid.com"}  host is optional
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="cfg/upload", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_data_snapshot():
	'''
	Force device data snapshot data, data example: {}
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="data/snapshot", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_data_query():
	'''
	Force upload device input data, data is device sn (vsn)
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="data/query", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_data_flush():
	'''
	Force flush buffered data, data example: {}
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="data/flush", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def send_output():
	'''
	Send device output value, data example:{ "device": "{DeviceID}", "output": "aaaa", "value": "dddd", "prop": "int_value"}
	:return:
	'''
	data = get_post_json_data()
	return send_action("output", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def send_command():
	'''
	Send device output value, data example:{ "device": "{DeviceID}", "cmd": "aaaa", "param": "eeee"}
	:return:
	'''
	data = get_post_json_data()
	return send_action("command", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def device_status(sn):
	'''
	Get device status
	:return: ONLINE/OFFLINE
	'''
	if frappe.session.user == "Guest":
		valid_auth_code()
	return frappe.get_value("IOT Device", sn, "device_status")

