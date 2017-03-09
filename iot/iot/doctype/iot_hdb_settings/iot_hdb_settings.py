# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class IOTHDBSettings(Document):

	@staticmethod
	def get_authorization_code():
		return frappe.db.get_single_value("IOT HDB Settings", "authorization_code")

	@staticmethod
	def get_on_behalf():
		return frappe.db.get_single_value("IOT HDB Settings", "on_behalf")

	@staticmethod
	def get_callback_url():
		url = frappe.db.get_single_value("IOT HDB Settings", "callback_url")
		if url == "":
			url = None
		return url

