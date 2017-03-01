# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _


def get_context(context):
	user_roles = frappe.get_roles(frappe.session.user)
	if 'IOT User' not in user_roles or frappe.session.user == 'Guest':
		raise frappe.PermissionError

	context.no_cache = 1
	context.show_sidebar = True
	context.no_breadcrumbs = False,

	new_flag = frappe.form_dict.new
	if new_flag:
		context.parents = [{"label": _("Back"), "route": frappe.get_request_header("referer")}]

		context.doc = {
			"name": _("Bunch Code"),
			"new_flag": new_flag,
			"owner_type": frappe.form_dict.type or "User",
			"owner_id": frappe.form_dict.owner or frappe.session.user
		}

		return

	bunch = frappe.form_dict.bunch or frappe.form_dict.name
	if not new_flag and not bunch:
		frappe.local.flags.redirect_location = "/me"
		raise frappe.Redirect

	doc = frappe.get_doc('IOT Device Bunch', bunch)
	if doc.owner_type == 'User':
		if doc.owner_id != frappe.session.user:
			raise frappe.PermissionError
	else:
		if not frappe.db.get_value("IOT UserGroup", {"group": doc.owner_id, "parent": frappe.session.user}):
			ent = frappe.db.get_value("IOT Employee Group", doc.owner_id, "parent")
			if frappe.db.get_value("IOT Enterprise", ent, "admin") != frappe.session.user:
				raise frappe.PermissionError

	doc.has_permission('read')

	if doc.owner_type == 'User':
		if (frappe.session.user == doc.owner_id):
			context.parents = [{"label": _("Your IOT Account"), "route": '/iot_me'}]
		else:
			context.parents = [{"label": _("IOT Account"), "route": '/iot_employee_group/' + doc.owner_id}]
	else:
		context.parents = [{"label": _("Employee Group"), "route": '/iot_employee_group/' + doc.owner_id}]

	context.doc = doc
