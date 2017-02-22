# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw, msgprint, _
from frappe.model.document import Document

class IOTUser(Document):
	def validate(self):
		if self.login_exits():
			frappe.throw(_("Login Name {0} already exists in Enterprise {1}").format(self.login_name, self.enterprise))

		# clear groups if Enterprise changed
		org_enterprise = frappe.db.get_value("IOT User", {"name": self.name}, "enterprise")
		if org_enterprise != self.enterprise:
			print('Remove all groups as the Enterpise is changed!')
			self.remove_all_groups()
		for g in self.group_assigned:
			print(g.group)

	def remove_all_groups(self):
		self.set("group_assigned", list(set(d for d in self.get("group_assigned") if d.group == "Guest")))

	def login_exits(self):
		return frappe.db.get_value("IOT User", {"login_name": self.login_name, "enterprise": self.enterprise, "name": ("!=", self.name)})

	def get_assigned_groups(self):
		"""Returns list of groups selected for that user"""
		return [d.group for d in self.group_assigned] if self.group_assigned else []


@frappe.whitelist()
def get_all_groups(enterprise):
	"""return all groups in specified enterprise"""
	groups = frappe.db.sql("""select name, grp_name, description
			from `tabIOT Employee Group`
			where parent = %(enterprise)s""", {"enterprise": enterprise}, as_dict=1)
	return groups

@frappe.whitelist()
def get_user_groups(arg=None):
	user = frappe.session.user
	if not user:
		frappe.throw(_("Authorization error"))
	"""get groups for a user"""
	if 'user' in frappe.form_dict:
		user = frappe.form_dict['user']

	groups = frappe.db.get_values("IOT UserGroup", {"parent": user}, "group")

	glist = []
	for g in groups:
		glist.append(frappe.db.get("IOT Employee Group", g[0]))
	return glist
	

@frappe.whitelist(allow_guest=True)
def ping():
	return 'pong'


