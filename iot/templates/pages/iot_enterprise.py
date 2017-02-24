# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json


def get_context(context):
	name = frappe.form_dict.enterprise or frappe.form_dict.name
	if not name:
		frappe.local.flags.redirect_location = "/me"
		raise frappe.Redirect

	user_roles = frappe.get_roles(frappe.session.user)
	if 'IOT User' not in user_roles or frappe.session.user == 'Guest':
		raise frappe.PermissionError

	context.no_cache = 1
	context.show_sidebar = True
	enterprise = frappe.get_doc('IOT Enterprise', name)
	if enterprise.get('admin') != frappe.session.user:
		raise frappe.PermissionError

	enterprise.has_permission('read')

	enterprise.users = get_users(enterprise.name, start=0, enabled=True, search=frappe.form_dict.get("search"))

	context.doc = enterprise


def get_users(enterprise, start=0, search=None, enabled=None):
	filters = {"enterprise": enterprise}
	if search:
		filters["user"] = ("like", "%{0}%".format(search))
	if enabled:
		filters["enabled"] = enabled

	users = frappe.get_all("IOT User", filters=filters,
		fields=["name", "login_name", "enabled", "modified"],
		limit_start=start, limit_page_length=10)

	for user in users:
		user.group_assigned = []
		groups = [d[0] for d in frappe.db.get_values('IOT UserGroup', {'parent': user.name}, "group"))
		for g in groups:
			gl = frappe.get_all('IOT Employee Group', filters={'name': g}, fields=["name", "description"])
			user.group_assigned.append(gl)

	return users
