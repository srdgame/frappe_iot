# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
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


def fire_raw_content(content, status=200, content_type='text/plain'):
	"""
	I am hack!!!
	:param content:
	:param content_type:
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


@frappe.whitelist(allow_guest=True)
def auth(username=None, password=None, topic=None, clientid=None, acc=None):
	username = username or frappe.form_dict.username
	password = password or frappe.form_dict.password
	topic = topic or frappe.form_dict.topic
	clientid = topic or frappe.form_dict.clientid
	acc = acc or frappe.form_dict.acc

	print("auth", username, password, topic, clientid, acc)
	print(frappe.form_dict)
	if username == 'root' and password == 'root':
		fire_raw_content("")
	else:
		fire_raw_content("Auth Error", 403)


@frappe.whitelist(allow_guest=True)
def superuser(username=None):
	username = username or frappe.form_dict.username
	print("superuser", username)
	print(frappe.form_dict)
	if username == "root":
		fire_raw_content("", 403)
	else:
		fire_raw_content("Auth Error", 403)


@frappe.whitelist(allow_guest=True)
def acl(username=None, topic=None, clientid=None, acc=None):
	username = username or frappe.form_dict.username
	topic = topic or frappe.form_dict.topic
	clientid = topic or frappe.form_dict.clientid
	acc = acc or frappe.form_dict.acc

	print("acl", username)
	print(frappe.form_dict)
	if username == 'root':
		fire_raw_content("")
	else:
		fire_raw_content("Auth Error", 403)


@frappe.whitelist(allow_guest=True)
def ping():
	return "mqtt_auth.pong"


