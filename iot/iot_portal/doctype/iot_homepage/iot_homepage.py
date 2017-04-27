# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.website.utils import delete_page_cache

class IOTHomepage(Document):
	def validate(self):
		if not self.description:
			self.description = frappe._("This is an example website auto-generated from IOT")
		delete_page_cache('iot_home')
