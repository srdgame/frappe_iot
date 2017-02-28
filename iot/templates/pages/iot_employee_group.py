# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json


def is_enterperise_admin(user, enterprise):
		return frappe.db.get_value("IOT Enterprise", {"name": enterprise, "admin": user}, "admin")


def get_context(context):
	name = frappe.form_dict.group or frappe.form_dict.name
	if not name:
		frappe.local.flags.redirect_location = "/me"
		raise frappe.Redirect

	user_roles = frappe.get_roles(frappe.session.user)
	if 'IOT User' not in user_roles or frappe.session.user == 'Guest':
		raise frappe.PermissionError

	context.no_cache = 1
	context.show_sidebar = True
	doc = frappe.get_doc('IOT Employee Group', name)
	if not is_enterperise_admin(frappe.session.user, doc.parent):
		raise frappe.PermissionError

	doc.has_permission('read')

	doc.users = get_users(doc.name, start=0, search=frappe.form_dict.get("search"))
	doc.bunch_codes = get_bunch_codes(doc.name, start=0, search=frappe.form_dict.get("search"))

	context.doc = doc


def get_users(group, start=0, search=None):
	filters = {"group": group}
	if search:
		filters["user"] = ("like", "%{0}%".format(search))

	user_names = frappe.get_all("IOT UserGroup", filters=filters,
		fields=["parent"],
		limit_start=start, limit_page_length=10)

	users = []
	for user in user_names:
		u = frappe.get_value("IOT User", user.parent, ["name", "enabled", "modified", "creation"])
		users.append({
			"name": u[0],
			"enabled": u[1],
			"modified": u[2],
			"creation": u[3]
		})

	return users


def get_bunch_codes(group, start=0, search=None):
	filters = {
		"owner_type": "IOT Employee Group",
		"owner_id": group
	}
	if search:
		filters["bunch_name"] = ("like", "%{0}%".format(search))

	bunch_codes = frappe.get_all("IOT Device Bunch", filters=filters,
		fields=["name", "bunch_name", "code", "modified", "creation"],
		limit_start=start, limit_page_length=10)


	return bunch_codes

