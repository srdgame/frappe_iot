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

		usr, domain = self.user.split('@')
		ent = frappe.db.get_value("IOT Enterprise", {"domain": domain})
		if ent and ent != self.enterprise:
			throw(_("Cannot add user {0} into {1} as Enterprise {2} has domain {3}").format(self.user, self.enterprise, ent, domain))

		# clear groups if Enterprise changed
		org_enterprise = frappe.db.get_value("IOT User", {"name": self.name}, "enterprise")
		if org_enterprise != self.enterprise:
			if frappe.db.get_value("IOT Enterprise", org_enterprise, "admin") == self.user:
				throw(_("User {0} is admin of Enterprise {1}, cannot remove it").format(self.user, org_enterprise))

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

	def update_enterprise(self, enterprise):
		self.set("enterprise", enterprise)
		self.save()

	def has_website_permission(self, ptype, verbose=False):
		"""Returns true if current user is the session user"""
		return self.user == frappe.session.user \
			   or frappe.get_value("IOT Enterprise", self.enterprise, "admin") == frappe.session.user


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
	session_user = frappe.session.user
	not_manager = 'IOT Manager' not in frappe.get_roles(session_user)
	if not_manager and session_user != user and frappe.get_value('IOT Enterprise', enterprise, 'admin') != session_user:
		throw(_("You do not permission for adding IOT User to {0}").format(enterprise))

	frappe.logger(__name__).info(_("Enable IOT User for {0} login_name {1}").format(user, login_name))

	# Set on behalf if user is not an IOT Manager
	if not_manager:
		frappe.session.user = "Administrator"

	if frappe.get_value("IOT User", user):
		throw(_("IOT User already exists!"))

	# Set proper Enterprise to user
	if not enterprise:
		usr, domain = user.split('@')
		enterprise = frappe.db.get_value("IOT Enterprise", {"domain": domain})
		if not enterprise:
			throw(_("No Enterprise for domain {0}").format(domain))

	doc = frappe.get_doc({
		"doctype": "IOT User",
		"enabled": True,
		"user": user,
		"enterprise": enterprise,
		# "login_name": login_name
		"login_name": "iMbEhIDE"  # login_name
	})
	doc.insert()

	# Rollback on behalf if user is not an IOT Manager
	if not_manager:
		frappe.session.user = session_user

	return doc


@frappe.whitelist()
def update_user(user=None, enabled=None, enterprise=None, login_name=None):
	session_user = frappe.session.user
	not_manager = 'IOT Manager' not in frappe.get_roles(session_user)
	if not_manager and session_user != user:
		frappe.throw(_("Your do not have permission to update IOT User {0}").format(user))

	frappe.logger(__name__).info(_("Enable IOT User for {0} login_name {1}").format(user, login_name))

	if enabled == "True":
		enabled = True

	# Set on behalf if user is not an IOT Manager
	if not_manager:
		frappe.session.user = "Administrator"

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
		frappe.session.user = session_user

	return doc


@frappe.whitelist()
def delete_user(user=None):
	session_user = frappe.session.user
	enterprise = frappe.get_value('IOT User', user, "enterprise")
	not_manager = 'IOT Manager' not in frappe.get_roles(session_user)
	if not_manager and session_user != user and frappe.get_value('IOT Enterprise', enterprise, 'admin') != session_user:
		throw(_("You do not permission for delete IOT User from {0}").format(enterprise))

	frappe.logger(__name__).info(_("Delete IOT User {0} from {1}").format(user, enterprise))

	frappe.delete_doc('IOT User', user, ignore_permissions=True)


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


