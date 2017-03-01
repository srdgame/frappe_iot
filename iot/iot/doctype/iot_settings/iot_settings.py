# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class IOTSettings(Document):
	@staticmethod
	def get_default_enterprise():
		return frappe.db.get_single_value("IOT Settings", "default_enterprise")