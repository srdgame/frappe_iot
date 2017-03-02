# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw, msgprint, _
from frappe.model.document import Document
from iot.iot.doctype.iot_user.iot_user import add_user, update_user


class IOTEnterprise(Document):
	def on_update(self):
		# TODO: We will not adding user automatically later, Enterprise Admin will do it manually.
		"""
		users = [d[0] for d in frappe.db.get_values("User", {"email": ("like", "%@{0}".format(self.domain))})]
		for user in users:
			add_user(user=user, enterprise=self.name)
		"""
		""" Add admin of enterprise automatically"""
		if self.get("admin") != self.admin:
			if frappe.get_value("IOT User", self.admin):
				update_user(user=self.admin, enterprise=self.name)
			else:
				add_user(user=self.admin, enterprise=self.name)

	def on_trash(self):
		users = [d[0] for d in frappe.db.get_values("IOT User", {"enterprise": self.name})]
		for user in users:
			try:
				frappe.delete_doc("IOT User", user)
			finally:
				print(_("Deleted Enterprise User {0}").format(user))
		frappe.db.commit()

	def remove_all_groups(self):
		self.set("groups", list(set(d for d in self.get("groups") if d.grp_name == "Guest")))

	def append_groups(self, *groups):
		"""Add groups to user"""
		current_groups = [d.grp_name for d in self.get("groups")]
		for group in groups:
			if group.grp_name in current_groups:
				continue
			self.append("groups", group)

	def add_groups(self, *groups):
		"""Add groups to user and save"""
		self.append_groups(*groups)
		self.save()

	def remove_groups(self, *groups):
		existing_groups = dict((d.grp_name, d) for d in self.get("groups"))
		for group in groups:
			if group.grp_name in existing_groups:
				self.get("groups").remove(existing_groups[group.grp_name])

		self.save()

	def group_exists(self, group_name):
		existing_groups = dict((d.grp_name, d) for d in self.get("groups"))
		return group_name in existing_groups

	def get_groups(self):
		"""Returns list of groups selected for that user"""
		return self.groups or []

	def has_website_permission(self, ptype, verbose=False):
		"""Returns true if admin is the session user"""
		if ptype == "read":
			return True
		return self.admin == frappe.session.user


def get_enterprise_list(doctype, txt, filters, limit_start, limit_page_length=20, order_by="modified desc"):
	return frappe.db.sql('''select *
		from `tabIOT Enterprise`
		where
			admin = %(user)s
			order by %(order_by)s
			limit {0}, {1}
		'''.format(limit_start, limit_page_length),
			{'user':frappe.session.user, 'order_by': order_by},
			as_dict=True,
			update={'doctype':'IOT Enterprise'})


def get_list_context(context=None):
	return {
		"show_sidebar": True,
		"show_search": True,
		"no_breadcrumbs": True,
		"title": _("Your Enteprises"),
		#"introduction": _('The IOT Enteprises those you can manage!'),
		"get_list": get_enterprise_list,
		"row_template": "templates/generators/iot_enterprise_row.html",
	}


def get_user_doc(user):
	"""
	Get User Document Object
	:param user: User's name
	:return: User Document Object
	"""
	user_doc = frappe.get_doc("IOT User", user)
	if not user_doc:
		throw(_("User {0} is not an IOT User").format(user))
	return user_doc


def get_ent_doc(enterprise=None):
	"""
	Get Enterprise Document for current user or specified Enterprise
	:param enterprise: Specified Enterprise Name
	:return: Enterprise Document Object
	"""
	user = frappe.session.user
	if not user:
		throw(_("Authorization error"))

	if 'IOT Manager' not in frappe.get_roles(user):
		user_doc = get_user_doc(user)

		if not enterprise:
			enterprise = user_doc.get("enterprise")

		"""Check Enterprise permission"""
		if user_doc.get("enterprise") != enterprise:
			throw(_("User {0} has no permission to access Enterprise {1}").format(user, enterprise))

	ent_doc = frappe.get_doc("IOT Enterprise", enterprise)
	if not ent_doc:
		throw(_("IOT Enterprise {0} does not exists!").format(enterprise))

	"""
	if ent_doc.get('admin') != user:
		if 'IOT Manager' not in frappe.get_roles(user):
			throw(_("User {0} has no permission to access Enterprise {1}").format(user, enterprise))
	"""

	return ent_doc


@frappe.whitelist()
def get_groups(enterprise=None):
	"""
	Get Groups of Specified Enterprise
	:param enterprise: Enterprise Name
	:return: Group object list
	"""
	ent_doc = get_ent_doc(enterprise)
	return ent_doc.get("groups")


def get_groups_2(enterprise=None):
	""" This the get_groups implementation using SQL"""
	user = frappe.session.user
	if 'IOT Manager' not in frappe.get_roles(user):
		user_doc = get_user_doc(user)
		if not enterprise:
			enterprise = user_doc.get("enterprise")

		if user_doc.get("enterprise") != enterprise:
			throw(_("User {0} has no permission to access Enterprise {1}").format(user, enterprise))

	"""return all groups in specified enterprise"""
	groups = frappe.db.sql("""select name, grp_name, description
			from `tabIOT Employee Group`
			where parent = %(enterprise)s""", {"enterprise": enterprise}, as_dict=1)
	return groups


@frappe.whitelist()
def add_groups(enterprise, groups):
	if not frappe.request.method == "POST":
		raise frappe.ValidationError

	user = frappe.session.user
	not_manager = 'IOT Manager' not in frappe.get_roles(user)
	if not_manager and frappe.db.get_value("IOT Enterprise", enterprise, "admin") != user:
		raise frappe.PermissionError

	ent_doc = get_ent_doc(enterprise)

	# Set proper doctype
	for g in groups:
		g["doctype"] = "IOT Employee Group"

	ent_doc.add_groups(groups)

	return "Done!"


@frappe.whitelist()
def get_enterprise(enterprise=None):
	"""Get Enterprise for current user"""
	return get_ent_doc(enterprise)


@frappe.whitelist(allow_guest=True)
def ping():
	return 'iot_enterprise pong'
