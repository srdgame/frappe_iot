# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt
#
# You need to using the mqtt auth plugin from:
#  https://github.com/symgrid/mosquitto-auth-plug
#  which has improve on acl with device id instead of ful topic

from __future__ import unicode_literals
import frappe
import json
import hashlib
from frappe import throw, msgprint, _


def get_post_json_data():
	if frappe.request.method != "POST":
		throw(_("Request Method Must be POST!"))
	ctype = frappe.get_request_header("Content-Type")
	if "json" not in ctype.lower():
		throw(_("Incorrect HTTP Content-Type found {0}").format(ctype))
	if not frappe.form_dict.data:
		throw(_("JSON Data not found!"))
	return json.loads(frappe.form_dict.data)


def fire_raw_content(status=200, content="", content_type='text/plain'):
	"""
	I am hack!!!
	:param status: HTTP Status Code
	:param content: HTTP Response Content
	:param content_type: HTTP Response Content Type
	:return:
	"""
	frappe.response['http_status_code'] = status
	frappe.response['filename'] = ''
	frappe.response['filecontent'] = content
	frappe.response['content_type'] = content_type
	frappe.response['type'] = 'download'
	if status != 200:
		frappe.local.is_ajax = True
		raise frappe.PermissionError


def http_200ok(info=""):
	fire_raw_content(status=200, content=info)


def http_403(err):
	fire_raw_content(status=403, content=err)


@frappe.whitelist(allow_guest=True)
def auth(username=None, password=None):
	username = username or frappe.form_dict.username
	password = password or frappe.form_dict.password
	print('auth', username, password)

	if username == 'root':
		root_password = frappe.db.get_single_value("IOT HDB Settings", "mqtt_root_password") or 'bXF0dF9pb3RfYWRtaW4K'
		if password == root_password:
			return http_200ok()
		else:
			return http_403("Auth Error")
	else:
		sid = frappe.db.get_single_value("IOT HDB Settings", "mqtt_device_password_sid") or 'ZGV2aWNlIGlkCg=='
		m = hashlib.md5()
		m.update(username + sid)
		if password == m.hexdigest():
			# TODO: for the one which is not in IOT Device should we check the frappe-make module to see if it is our device?
			if frappe.get_value("IOT Device", username, "enabled") == 1:
				return http_200ok()
			else:
				return http_403("Auth Error")
		else:
			try:
				frappe.local.login_manager.authenticate(username, password)
				if frappe.local.login_manager.user == username:
					return http_200ok()
				else:
					return http_403("Auth Error")
			except Exception as ex:
				return http_403("Auth Error")

	return http_403("Auth Error")


@frappe.whitelist(allow_guest=True)
def superuser(username=None):
	username = username or frappe.form_dict.username
	print('superuser', username)
	if username == "root":
		return http_200ok()
	else:
		return http_403("Auth Error")


@frappe.whitelist(allow_guest=True)
def acl(username=None, topic=None, clientid=None, acc=None):
	username = username or frappe.form_dict.username
	topic = topic or frappe.form_dict.topic # via our auth plugin, this topic is the device id only
	clientid = clientid or frappe.form_dict.clientid
	acc = acc or frappe.form_dict.acc
	print('acl', username, topic, clientid, acc)

	if username == 'root':
		return http_200ok()
	else:
		try:
			dev = frappe.get_doc("IOT Device", topic)
			print(dev.list_owners())
			if username in dev.list_owners():
				return http_200ok()
			else:
				return http_403("Auth Error")
		except Exception as ex:
			return http_403("Auth Error")

	return http_403("Auth Error")


@frappe.whitelist(allow_guest=True)
def ping():
	return "mqtt_auth.pong"


