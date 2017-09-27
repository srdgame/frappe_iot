# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import redis
import requests
import datetime
import uuid
from frappe.utils import now, get_datetime, convert_utc_to_user_timezone
from frappe import throw, msgprint, _, _dict
from iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings
from hdb_api import valid_auth_code


@frappe.whitelist()
def redis_status():
	from iot.doctype.iot_hdb_settings.iot_hdb_settings import get_redis_status
	return get_redis_status()


@frappe.whitelist()
def influxdb_status():
	from iot.doctype.iot_hdb_settings.iot_hdb_settings import get_influxdb_status
	return get_influxdb_status()


@frappe.whitelist()
def iot_device_data_f(sn=None, vsn=None):
	return json.load(open('/home/frappe/frappe-bench/sites/test/public/files/data.json'))


@frappe.whitelist()
def iot_device_data(sn=None, vsn=None):
	sn = sn or frappe.form_dict.get('sn')
	vsn = vsn or sn
	doc = frappe.get_doc('IOT Device', sn)
	doc.has_permission("read")

	if vsn != sn:
		if vsn not in iot_device_tree(sn):
			return ""

	cfg = iot_device_cfg(sn, vsn)
	if not cfg:
		return ""
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/12")
	hs = client.hgetall(vsn)
	data = {}
	if cfg.has_key("inputs"):
		inputs = cfg.get("inputs")
		for input in inputs:
			s = hs.get(input + "/value")
			if s:
				val = json.loads(s)
				data[input] = {"PV": val[1], "TM": val[0], "Q": val[2]}

	return data


@frappe.whitelist()
def iot_device_data_array(sn=None, vsn=None):
	sn = sn or frappe.form_dict.get('sn')
	vsn = vsn or sn
	doc = frappe.get_doc('IOT Device', sn)
	doc.has_permission("read")

	if vsn != sn:
		if vsn not in iot_device_tree(sn):
			return ""

	cfg = iot_device_cfg(sn, vsn)
	if not cfg:
		return ""

	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/12")
	hs = client.hgetall(vsn)
	data = []

	if cfg.has_key("inputs"):
		inputs = cfg.get("inputs")
		for input in inputs:
			s = hs.get(input + "/value")
			if not s:
				continue
			val = json.loads(hs.get(input + "/value"))
			ts = datetime.datetime.utcfromtimestamp(int(int(val[0]) / 1000))
			timestr = str(convert_utc_to_user_timezone(ts).replace(tzinfo=None))
			data.append({"NAME": input, "PV": val[1], "TM": timestr, "Q": val[1]})

	return data


@frappe.whitelist()
def iot_device_his_data(key, sn, vsn=None, fields="*", condition=None):
	vsn = vsn or sn
	doc = frappe.get_doc('IOT Device', sn)
	doc.has_permission("read")

	if vsn != sn:
		if vsn not in iot_device_tree(sn):
			return 401

	inf_server = IOTHDBSettings.get_influxdb_server()
	if not inf_server:
		frappe.logger(__name__).error("InfluxDB Configuration missing in IOTHDBSettings")
		return 500
	query = 'SELECT ' + fields + ' FROM "' + key + '" WHERE device=\'' + vsn + '\''
	if condition:
		query = query + condition
	else:
		query = query + " ORDER BY time DESC LIMIT 1000"

	domain = frappe.get_value("Cloud Company", doc.company, "domain")
	r = requests.session().get(inf_server + "/query", params={"q": query, "db": domain}, timeout=10)
	if r.status_code == 200:
		return r.json()["results"] or r.json()

	return r.text


@frappe.whitelist()
def iot_device_tree(sn=None):
	sn = sn or frappe.form_dict.get('sn')
	doc = frappe.get_doc('IOT Device', sn)
	doc.has_permission("read")
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/11")
	return client.lrange(sn, 0, -1)


@frappe.whitelist()
def iot_device_cfg(sn=None, vsn=None):
	sn = sn or frappe.form_dict.get('sn')
	doc = frappe.get_doc('IOT Device', sn)
	doc.has_permission("read")
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/10")
	return json.loads(client.get(vsn or sn) or "")


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
def ping():
	form_data = frappe.form_dict
	if frappe.request and frappe.request.method == "POST":
		if form_data.data:
			form_data = json.loads(form_data.data)
		return form_data.get("text") or "No Text"
	return 'pong'
