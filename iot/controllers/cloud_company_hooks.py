# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests
import time
from frappe import _, throw
from iot.iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings


def after_insert(doc, method):
	frappe.enqueue('iot.controllers.cloud_company_hooks.create_influxdb', db_name=doc.domain)


def create_influxdb(db_name, max_retry=10, sleep=None):
	if sleep:
		time.sleep(sleep)
	max_retry = max_retry - 1

	inf_server = IOTHDBSettings.get_influxdb_server()
	if not inf_server:
		frappe.logger(__name__).error("InfluxDB Configuration missing in IOTHDBSettings")
		return

	try:
		r = requests.session().get(inf_server + "/query", params={"q": ('''CREATE DATABASE "{0}"''').format(db_name)}, timeout=1)

		if r.status_code != 200:
			frappe.logger(__name__).error(r.text)
			if max_retry > 0:
				frappe.enqueue('iot.controllers.cloud_company_hooks.create_influxdb', db_name=db_name, max_retry=max_retry, sleep=60)
			throw(r.text)
		else:
			frappe.logger(__name__).debug(r.text)
	except Exception as ex:
		frappe.logger(__name__).error(ex)
		if max_retry > 0:
			frappe.enqueue('iot.controllers.cloud_company_hooks.create_influxdb', db_name=db_name, max_retry=max_retry, sleep=60)
		throw(repr(ex))