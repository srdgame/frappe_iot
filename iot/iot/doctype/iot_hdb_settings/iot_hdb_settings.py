# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import re
import redis
import requests
from frappe import throw, _
from frappe.model.document import Document


class IOTHDBSettings(Document):
	def validate(self):
		if self.enable_default_bunch_code and not self.default_bunch_code:
			throw(_("Default Bunch Code Missing"))

	def update_redis_status(self, status):
		if self.redis_status == status:
			return
		self.redis_status = status
		self.redis_updated = frappe.utils.now()
		self.save()

	def update_influxdb_status(self, status):
		if self.influxdb_status == status:
			return
		self.influxdb_status = status
		self.influxdb_updated = frappe.utils.now()
		self.save()

	def update_hdb_status(self, status):
		if self.hdb_status == status:
			return
		self.hdb_status = status
		self.hdb_updated = frappe.utils.now()
		self.save()

	def refresh_status(self):
		#frappe.enqueue('iot.iot.doctype.iot_hdb_settings.iot_hdb_settings.get_hdb_status')
		get_hdb_status()

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
		return frappe.db.get_single_value("IOT HDB Settings", "default_bunch_code")

	@staticmethod
	def is_default_bunch_enabled():
		return frappe.db.get_single_value("IOT HDB Settings", "enable_default_bunch_code")


def gen_server_url(server, protocol=None, port=None):
	mport = re.search(":(\d+)$", server)
	mprotocol = re.search("^(.+)://", server)
	if not mprotocol and protocol:
		server = protocol + "://" + server
	if not mport and port:
		server = server + ":" + port
	return server


def get_redis_status():
	try:
		client = redis.Redis.from_url(IOTHDBSettings.get_redis_server(), socket_timeout=0.1,
									  socket_connect_timeout=0.1)
		return client.ping()
	except Exception:
		return False


def get_influxdb_status():
	try:
		inf_server = IOTHDBSettings.get_influxdb_server()
		if not inf_server:
			frappe.logger(__name__).error("InfluxDB Configuration missing in IOTHDBSettings")
			return

		r = requests.session().get(inf_server + "/query", params={"q": '''SHOW USERS'''}, timeout=1)
		return r.status_code == 200
	except Exception:
		return False


def get_hdb_status():
	doc = frappe.get_single("IOT HDB Settings")

	status = get_redis_status()
	if status:
		doc.update_redis_status("ON")
	else:
		doc.update_redis_status("OFF")

	status = get_influxdb_status()
	if status:
		doc.update_influxdb_status("ON")
	else:
		doc.update_influxdb_status("OFF")
