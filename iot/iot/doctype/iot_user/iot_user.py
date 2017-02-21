# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class IOTUser(Document):
	__org_enterprise = None

	def onload(self):
		self.__org_enterprise = self.enterprise

	def autoname(self):
		"""set name as <Login Name>@<Enterprise Domain>"""
		domain = frappe.db.get_value("IOT Enterprise", {"name": self.enterprise}, "domain")
		self.name = self.login_name + domain

	def validate(self):
		# clear groups if Enterprise changed
		if self.__org_enterprise != self.enterprise:
			self.remove_all_groups()

	def remove_all_groups(self):
		self.set("group_assigned", list(set(d for d in self.get("group_assigned") if d.group == "Guest")))


@frappe.whitelist()
def get_all_groups(enterprise='SymTech'):
	"""return all groups in specified enterprise"""
	groups = frappe.db.sql("""select name, grp_name
			from `tabIOT Employee Group`
			where parent = %(enterprise)s""", {"enterprise": enterprise}, as_dict=1)
	return groups

@frappe.whitelist(allow_guest=True)
def ping():
	return 'pong'


