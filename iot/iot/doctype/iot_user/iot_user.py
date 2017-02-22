# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw, msgprint, _
from frappe.model.document import Document

class IOTUser(Document):
	def validate(self):
		if self.login_exists():
			throw(_("Login Name {0} already exists in Enterprise {1}").format(self.login_name, self.enterprise))

		# clear groups if Enterprise changed
		org_enterprise = frappe.db.get_value("IOT User", {"name": self.name}, "enterprise")
		if org_enterprise != self.enterprise:
			print('Remove all groups as the Enterpise is changed!')
			self.remove_all_groups()
		for g in self.group_assigned:
			print(g.group)

	def remove_all_groups(self):
		self.set("group_assigned", list(set(d for d in self.get("group_assigned") if d.group == "Guest")))

	def append_groups(self, *groups):
		"""Add groups to user"""
		current_groups = [d.group for d in self.get("group_assigned")]
		for group in groups:
			if group in current_groups:
				continue
			self.append("group_assigned", {"group": group})

	def add_groups(self, *groups):
		"""Add groups to user and save"""
		self.append_groups(*groups)
		self.save()

	def remove_groups(self, *groups):
		existing_groups = dict((d.group, d) for d in self.get("group_assigned"))
		for group in groups:
			if group in existing_groups:
				self.get("group_assigned").remove(existing_groups[group])

		self.save()

	def login_exists(self):
		return frappe.db.get_value("IOT User", {"login_name": self.login_name, "enterprise": self.enterprise, "name": ("!=", self.name)})

	def get_groups(self):
		"""Returns list of groups selected for that user"""
		return [d.group for d in self.group_assigned] if self.group_assigned else []

def get_valid_user():
	user = frappe.session.user
	if not user:
		throw(_("Authorization error"))

	if 'uid' in frappe.form_dict:
		if 'IOT Manager' in frappe.get_roles(user):
			user = frappe.form_dict['uid']
		else:
			throw(_("You are not IOT Mananger, cannot accessing other user's group settings"))

	return user

@frappe.whitelist()
def get_groups(arg=None):
	"""get groups for a user"""
	user = get_valid_user()
	groups = frappe.db.get_values("IOT UserGroup", {"parent": user}, "group")

	group_list = []
	for g in groups:
		group_list.append(frappe.db.get("IOT Employee Group", g[0]))
	return group_list

@frappe.whitelist()
def add_groups(groups):
	user = get_valid_user()
	user_doc = frappe.get_doc("IOT User", user)
	user_doc.add_groups(groups)

@frappe.whitelist()
def remove_groups(groups):
	user = get_valid_user()
	user_doc = frappe.get_doc("IOT User", user)
	user_doc.remove_groups(groups)

@frappe.whitelist(allow_guest=True)
def ping():
	return 'pong'


