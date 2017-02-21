# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class IOTUser(Document):
	def onload(self):
		login, domain = self.login_name.split('@')
		self.login_name = login

	def validate(self):
		# check for login name
		org_login = frappe.db.get_value("IOT User", {"name": self.name},
		org_enterprise = frappe.db.get_value("IOT User", {"name": self.name}, "enterprise")
		if org_login != self.login_name or org_enterprise != self.enterprise:
			domain = frappe.db.get_value("IOT Enterprise", {"name": self.enterprise}, "domain")
			login = self.login_name + '@' + domain
			existing = frappe.db.get_value("IOT User", {"login_name", login}, "name")
			if existing:
				frappe.throw(_("Login name {0} already exists in Enterprise {1}").format(self.login_name, self.enterprise))
			self.login_name = login
		
		# clear groups if Enterprise changed
		if org_enterprise != self.enterprise:
			print('Remove all groups as the Enterpise is changed!')
			self.remove_all_groups()

	def remove_all_groups(self):
		self.set("group_assigned", list(set(d for d in self.get("group_assigned") if d.group == "Guest")))


@frappe.whitelist()
def get_all_groups(enterprise='SymTech'):
	"""return all groups in specified enterprise"""
	groups = frappe.db.sql("""select name, grp_name, description
			from `tabIOT Employee Group`
			where parent = %(enterprise)s""", {"enterprise": enterprise}, as_dict=1)
	return groups

@frappe.whitelist(allow_guest=True)
def ping():
	return 'pong'


