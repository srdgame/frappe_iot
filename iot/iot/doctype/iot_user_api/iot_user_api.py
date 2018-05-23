# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import redis
from frappe.model.document import Document
from iot.iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings
from cloud.cloud.doctype.cloud_company.cloud_company import list_admin_companies


class IOTUserApi(Document):
	def update(self):
		self.enable_statistics(1)

	def on_trash(self):
		self.enable_statistics(0)

	def enable_statistics(self, enable):
		companies = list_admin_companies(self.user)
		if len(companies) == 0:
			return

		client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/14")

		for company in companies:
			doc = frappe.get_doc('Cloud Company', company)
			client.hmset(doc.domain, {
				'company': doc.name,
				'auth_code': self.authorization_code,
				'database': doc.domain,
				'enable': enable,
			})
