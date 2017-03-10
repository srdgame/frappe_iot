# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import requests
from frappe import throw, msgprint, _
from frappe.utils import cint
from frappe.model.document import Document
from iot.doctype.iot_device.iot_device import IOTDevice
from iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings
from hdb_api import valid_auth_code

@frappe.whitelist(allow_guest=True)
def iot_device_data_hdb(sn=None):
	valid_auth_code()
	user = frappe.session.user
	sn = sn or frappe.form_dict.get('sn')
	doc = frappe.get_doc('IOT Device', sn)
	session = requests.session()
	url = IOTHDBSettings.get_data_url() + "/rtdb/" + doc.dev_name
	return session.get(url).json()


@frappe.whitelist()
def iot_device_data(sn=None):
	user = frappe.session.user
	sn = sn or frappe.form_dict.get('sn')
	doc = frappe.get_doc('IOT Device', sn)
	doc.has_permission("read")
	session = requests.session()
	url = IOTHDBSettings.get_data_url() + "/rtdb/" + doc.dev_name
	return session.get(url).json()


def get_post_json_data():
	if frappe.request.method != "POST":
		throw(_("Request Method Must be POST!"))
	ctype = frappe.get_request_header("Content-Type")
	if "json" not in ctype.lower():
		throw(_("Incorrect HTTP Content-Type found {0}").format(ctype))
	if not frappe.form_dict.data:
		throw(_("JSON Data not found!"))
	return json.loads(frappe.form_dict.data)


def fire_callback(cb_url, cb_data):
	frappe.logger(__name__).debug("HDB Fire Callback with data:")
	frappe.logger(__name__).debug(cb_data)
	session = requests.session()
	r = session.post(cb_url, json=cb_data)

	if r.status_code != 200:
		frappe.logger(__name__).error(r.text)
	else:
		frappe.logger(__name__).debug(r.text)


@frappe.whitelist()
def iot_device_ctrl(cmds=None):
	cmds = cmds or get_post_json_data()
	for cmd in cmds:
		doc = frappe.get_doc('IOT Device', cmd.sn)
		doc.has_permission("write")

	url = IOTHDBSettings.get_data_url() + "/iocmd"
	session = requests.session()
	return session.post(url, json={
		"cmds": cmds
	})


@frappe.whitelist(allow_guest=True)
def ping():
	form_data = frappe.form_dict
	if frappe.request and frappe.request.method == "POST":
		if form_data.data:
			form_data = json.loads(form_data.data)
		return form_data.get("text") or "No Text"
	return 'pong'


