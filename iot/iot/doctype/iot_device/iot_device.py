# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import now, get_datetime, cstr


class IOTDevice(Document):
	def update_status(self, status):
		""" update device status """
		self.set("status", status)
		self.set("last_updated", now())
		self.save()

	def update_bunch(self, bunch):
		""" update device bunch code """
		self.set("bunch", bunch)
		self.set("last_updated", now())
		self.save()

	@staticmethod
	def check_sn_exists(sn):
		return frappe.db.get_value("IOT Device", {"sn": sn}, "sn")

	@staticmethod
	def list_device_sn_by_bunch(bunch):
		return [d[0] for d in frappe.db.get_values("IOT Device", {"bunch": bunch}, "sn")]

	@staticmethod
	def get_device_doc(sn):
		try:
			return frappe.get_doc("IOT Device", sn)
		finally:
			return

