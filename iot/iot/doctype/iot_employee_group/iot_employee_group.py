# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class IOTEmployeeGroup(Document):

	def autoname(self):
		"""set name as [self.parent].<name>"""
		self.grp_name = self.grp_name.strip()
		self.name = '[' + self.parent + '].' + self.grp_name

	def on_trash(self):
		for d in frappe.get_all("IOT UserGroup", {"group": self.name}):
			d.delete()

	def has_website_permission(self, ptype, verbose=False):
		"""Returns true if current user is the session user"""
		admin = frappe.get_value("IOT Enterprise", self.parent, "admin")
		return admin == frappe.session.user
