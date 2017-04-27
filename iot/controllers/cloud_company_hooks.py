# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import requests
from iot.iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings

def after_insert(doc, method):
	inf_server = IOTHDBSettings.get_influxdb_server()
	session = requests.session()
	url = inf_server + "/query"
	params = {
		"q": ('''CREATE DATABASE "{0}"''').format(doc.domain)
	}
	r = session.get(url, params=params)

	if r.status_code != 200:
		frappe.logger(__name__).error(r.text)
		frappe.throw(r.text)
	else:
		frappe.logger(__name__).debug(r.text)