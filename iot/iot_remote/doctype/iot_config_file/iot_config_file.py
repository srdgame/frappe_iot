# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class IOTConfigFile(Document):
	def validate(self):
		self.config_name = frappe.get_value("IOT Config", self.config, "config_name")
		self.owner_name = frappe.get_value("IOT Config", self.config, "owner_name")
		self.file_url = "/iot_configs/{0}/v_{1}".format(self.config_name.strip().lower().replace(' ','_'), self.version)