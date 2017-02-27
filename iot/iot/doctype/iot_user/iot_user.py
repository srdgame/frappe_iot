# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw, msgprint, _
from frappe.model.document import Document

class IOTUser(Document):
	def __setup__(self):
		# because it is handled separately
		def_ent = frappe.db.get_single_value("IOT Settings", "default_enterprise")
		if def_ent:
			self.enterprise = def_ent

	def validate(self):
		if self.login_exists():
			throw(_("Login Name {0} already exists in Enterprise {1}").format(self.login_name, self.enterprise))

		# clear groups if Enterprise changed
		org_enterprise = frappe.db.get_value("IOT User", {"name": self.name}, "enterprise")
		if org_enterprise != self.enterprise:
			print('Remove all groups as the Enterpise is changed!')
			self.remove_all_groups()

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
		# hack login_name
		if self.login_name == "iMbEhIDE":
			return False
		return frappe.db.get_value("IOT User", {"login_name": self.login_name, "enterprise": self.enterprise, "name": ("!=", self.name)})

	def get_groups(self):
		"""Returns list of groups selected for that user"""
		return [d.group for d in self.group_assigned] if self.group_assigned else []


@frappe.whitelist()
def add_user(user=None, enterprise=None, login_name=None):
	"""
	This is used for page form enable on IOT User, which is adding one IOT User DocType document
	:param enabled:
	:param user: 
	:param enterprise: 
	:param login_name: 
	:return: 
	"""
	if not frappe.request.method == "POST":
		raise frappe.ValidationError

	not_manager = 'IOT Manager' not in frappe.get_roles(user)
	if not_manager and frappe.session.user != user:
		raise frappe.PermissionError

	frappe.logger(__name__).info(_("Enable IOT User for {0} login_name {1}").format(user, login_name))

	# Set on behalf if user is not an IOT Manager
	if not_manager:
		frappe.session.user = frappe.db.get_single_value("IOT HDB Settings", "on_behalf") or "Administrator"

	doc = frappe.get_doc({
		"doctype": "IOT User",
		"user": user,
		"enterprise": enterprise,
		"login_name": login_name
	})
	doc.insert()

	# Rollback on behalf if user is not an IOT Manager
	if not_manager:
		frappe.session.user = user

	return {"result": True, "data": doc}


@frappe.whitelist()
def update_user(user=None, enabled=None, enterprise=None, login_name=None):
	if not frappe.request.method == "POST":
		raise frappe.ValidationError

	not_manager = 'IOT Manager' not in frappe.get_roles(user)
	if not_manager and frappe.session.user != user:
		raise frappe.PermissionError

	frappe.logger(__name__).info(_("Enable IOT User for {0} login_name {1}").format(user, login_name))

	if enabled == "True":
		enabled = True

	# Set on behalf if user is not an IOT Manager
	if not_manager:
		frappe.session.user = frappe.db.get_single_value("IOT HDB Settings", "on_behalf") or "Administrator"

	doc = frappe.get_doc('IOT User', user)
	if enabled is not None:
		doc.set("enable", enabled)
	if enterprise is not None:
		doc.set("enterprise", enterprise)
	if login_name is not None:
		doc.set("login_name", login_name)
	doc.save()

	# Rollback on behalf if user is not an IOT Manager
	if not_manager:
		frappe.session.user = user

	return {"result": True, "data": doc}


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


