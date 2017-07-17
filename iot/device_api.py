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
def get_action_result(id):
	if frappe.session.user == "Guest":
		valid_auth_code()
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/7")
	str = client.get(id)
	if str:
		return json.loads(str)


@frappe.whitelist(allow_guest=True)
def send_action(action):
	if frappe.session.user == "Guest":
		valid_auth_code()
	data = get_post_json_data()

	if not data.get("device"):
		throw(_("Device SN does not exits!"))
	doc = frappe.get_doc("IOT Device", data.get("device"))
	if not doc.has_permission("write"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	if not data.get("id"):
		data["id"] = str(uuid.uuid1()).upper()

	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server())
	r = client.publish("device_" + action, json.dumps(data))
	if r <= 0:
		throw(_("Redis message published, but no listener!"))
	return data["id"]


@frappe.whitelist(allow_guest=True)
def app_install():
	if frappe.session.user == "Guest":
		valid_auth_code()
	data = get_post_json_data()
	data.update({
		"topic": "install"
	})
	return send_action("app", data)


@frappe.whitelist(allow_guest=True)
def app_uninstall():
	if frappe.session.user == "Guest":
		valid_auth_code()
	data = get_post_json_data()
	data.update({
		"topic": "uninstall"
	})
	return send_action("app", data)


@frappe.whitelist(allow_guest=True)
def app_upgrade():
	if frappe.session.user == "Guest":
		valid_auth_code()
	data = get_post_json_data()
	data.update({
		"topic": "upgrade"
	})
	return send_action("app", data)


@frappe.whitelist(allow_guest=True)
def sys_upgrade():
	if frappe.session.user == "Guest":
		valid_auth_code()
	data = get_post_json_data()
	data.update({
		"topic": "upgrade"
	})
	return send_action("sys", data)


@frappe.whitelist(allow_guest=True)
def sys_enable_data():
	if frappe.session.user == "Guest":
		valid_auth_code()
	data = get_post_json_data()
	data.update({
		"topic": "enable/data"
	})
	return send_action("sys", data)


@frappe.whitelist(allow_guest=True)
def sys_enable_log():
	if frappe.session.user == "Guest":
		valid_auth_code()
	data = get_post_json_data()
	data.update({
		"topic": "enable/log"
	})
	return send_action("sys", data)


@frappe.whitelist(allow_guest=True)
def sys_enable_comm():
	if frappe.session.user == "Guest":
		valid_auth_code()
	data = get_post_json_data()
	data.update({
		"topic": "enable/comm"
	})
	return send_action("sys", data)


@frappe.whitelist(allow_guest=True)
def send_output():
	if frappe.session.user == "Guest":
		valid_auth_code()
	data = get_post_json_data()
	# data.update({
	# 	"topic": "enable/comm"
	# })
	return send_action("output", data)


@frappe.whitelist(allow_guest=True)
def send_command():
	if frappe.session.user == "Guest":
		valid_auth_code()
	data = get_post_json_data()
	# data.update({
	# 	"topic": "enable/comm"
	# })
	return send_action("command", data)