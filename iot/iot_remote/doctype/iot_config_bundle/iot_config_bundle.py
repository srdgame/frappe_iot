# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class IOTConfigBundle(Document):
	def validate(self):
		for dev in self.devices:
			dev.device_name = frappe.get_value("IOT Device", dev.device, "dev_name")
