# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import re
from frappe.model.document import Document


class IOTHDBSettings(Document):

	@staticmethod
	def get_on_behalf(auth_code):
		if frappe.db.get_single_value("IOT HDB Settings", "authorization_code") == auth_code:
			return frappe.db.get_single_value("IOT HDB Settings", "on_behalf")
		return None

	@staticmethod
	def get_redis_server():
		url = frappe.db.get_single_value("IOT HDB Settings", "redis_server")
		if not url:
			return None
		return gen_server_url(url, "reids", 6379)

	@staticmethod
	def get_influxdb_server():
		url = frappe.db.get_single_value("IOT HDB Settings", "influxdb_server")
		if not url:
			return None
		return gen_server_url(url, "http", 8086)


	@staticmethod
	def get_default_bunch():
		bunch = frappe.db.get_single_value("IOT HDB Settings", "default_bunch_code")
		if bunch == "":
			bunch = None
		return bunch


def gen_server_url(server, protocol=None, port=None):
	mport = re.search(":(\d+)$", server)
	mprotocol = re.search("^(.+)://", server)
	if not mprotocol and protocol:
		server = protocol + "://" + server
	if not mport and port:
		server = server + ":" + port
	return server
