# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import redis
import uuid
from frappe import throw, msgprint, _
from iot.doctype.iot_device.iot_device import IOTDevice
from iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings


def valid_auth_code():
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
	return json.loads(data)


@frappe.whitelist(allow_guest=True)
def get_action_result(id):
	if frappe.session.user == "Guest":
		valid_auth_code()
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/7")
	str = client.get(id)
	if str:
		return json.loads(str)


def add_device_action_log(dev_doc, channel, action, id, data, status="Success", message=None):
	frappe.get_doc({
		"doctype": "IOT Device Activity",
		"user": frappe.session.user,
		"status": status,
		"operation": "Action",
		"subject": _("Device action {0} - {1}").format(channel, action),
		"device": dev_doc.name,
		"owner_type": dev_doc.owner_type,
		"owner_id": dev_doc.owner_id,
		"owner_company": dev_doc.company,
		"message": json.dumps({
			"channel": channel,
			"action": action,
			"id": id,
			"data": data,
			"message": message
		})
	}).insert(ignore_permissions=True)


@frappe.whitelist(allow_guest=True)
def send_action(channel, action=None, id=None, device=None, data=None):
	if frappe.session.user == "Guest":
		valid_auth_code()
	data = data or get_post_json_data()
	id = id or str(uuid.uuid1()).upper()

	if not device:
		throw(_("Device SN does not exits!"))

	doc = frappe.get_doc("IOT Device", device)
	if not doc.has_permission("write"):
		add_device_action_log(doc, channel, action, id, data, "Failed", "Permission error")
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server())
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
	Query application log, data example: {"inst": "bms", "option": "auto", "value": 1}
	:return:
	'''
	data = get_post_json_data()
	return send_action("app", action="option", id=data.get("id"), device=data.get("device"), data=data.get("data"))


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
def sys_reboot():
	'''
	Reboot device.
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="reboot", id=data.get("id"), device=data.get("device"), data=data.get("data"))


@frappe.whitelist(allow_guest=True)
def sys_quit():
	'''
	Quit our iot application which will cause an new application run in our device.
	:return:
	'''
	data = get_post_json_data()
	return send_action("sys", action="quit", id=data.get("id"), device=data.get("device"), data=data.get("data"))


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