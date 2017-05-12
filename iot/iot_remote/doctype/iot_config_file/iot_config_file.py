# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import get_fullname


class IOTConfigFile(Document):
	def validate(self):
		if self.owner_type == 'Cloud Company Group':
			self.owner_name = frappe.get_value(self.owner_type, self.owner_id, "group_name")
		else:
			self.owner_name = get_fullname(self.owner_id)
