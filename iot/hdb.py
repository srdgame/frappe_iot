# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import redis
import requests
from frappe import throw, msgprint, _, _dict
from iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings


@frappe.whitelist(allow_guest=True)
def iot_device_data_hdb(sn=None):
	# valid_auth_code()
	sn = sn or frappe.form_dict.get('sn')
	doc = frappe.get_doc('IOT Device', sn)



@frappe.whitelist()
def iot_device_data(sn=None, vsn=None):
	sn = sn or frappe.form_dict.get('sn')
	vsn = vsn or sn
	doc = frappe.get_doc('IOT Device', sn)
	doc.has_permission("read")
	cfg = iot_device_cfg(sn)
	if not cfg:
		return ""

	tags = json.loads(cfg).get("tags")
	if vsn != sn:
		if vsn not in iot_device_tree(sn):
			return ""

	client = redis.Redis.from_url(IOTHDBSettings.get_data_url() + "/2")
	hs = client.hgetall(sn)
	data = {}
	for tag in tags:
		name = tag.get('name')
		data[name] = {
			"PV": hs.get(name + ".PV"),
			"TM": hs.get(name + ".TM"),
			"Q": hs.get(name + ".Q"),
		}

	return data


@frappe.whitelist()
def iot_device_tree(sn=None):
	sn = sn or frappe.form_dict.get('sn')
	doc = frappe.get_doc('IOT Device', sn)
	doc.has_permission("read")
	client = redis.Redis.from_url(IOTHDBSettings.get_data_url() + "/1")
	return client.lrange(sn, 0, -1)


@frappe.whitelist()
def iot_device_cfg(sn=None):
	sn = sn or frappe.form_dict.get('sn')
	doc = frappe.get_doc('IOT Device', sn)
	doc.has_permission("read")
	client = redis.Redis.from_url(IOTHDBSettings.get_data_url() + "/0")
	return client.get(sn)


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
def iot_device_ctrl(ctrl=None):
	ctrl = ctrl or get_post_json_data()
	cmds = []
	for cmd in ctrl:
		doc = frappe.get_doc('IOT Device', cmd.sn)
		doc.has_permission("write")
		cmds.append({
			"boxname": doc.dev_name,
			"boxsn": cmd.sn,
			"ctrl": cmd.ctrl,
			"tag": cmd.tag,
			"uflg": cmd.uflg,
			"val": cmd.val,
			"vt": cmd.vt
		})

	url = IOTHDBSettings.get_data_url() + "/iocmd"
	session = requests.session()
	r = session.post(url, json={
		"cmds": cmds
	})
	if r:
		return r.json();


@frappe.whitelist(allow_guest=True)
def ping():
	form_data = frappe.form_dict
	if frappe.request and frappe.request.method == "POST":
		if form_data.data:
			form_data = json.loads(form_data.data)
		return form_data.get("text") or "No Text"
	return 'pong'


