# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json


def get_context(context):
	user_roles = frappe.get_roles(frappe.session.user)
	if 'IOT User' not in user_roles or frappe.session.user == 'Guest':
		raise frappe.PermissionError

	new_flag = frappe.form_dict.new
	bunch = frappe.form_dict.bunch
	if not new_flag and not bunch:
		frappe.local.flags.redirect_location = "/me"
		raise frappe.Redirect

	context.no_cache = 1
	context.show_sidebar = True
	doc = frappe.get_doc('IOT Device Bunch', bunch)
	if doc.owner_type == 'User':
		if doc.owner_id != frappe.session.user:
			raise frappe.PermissionError
	else:
		if not frappe.db.get_value("IOT UserGroup", {"group": doc.owner_id, "parent": frappe.session.user})
			ent = frappe.db.get_value("IOT Employee Group", doc.owner_id, "parent")
			if frappe.db.get_value("IOT Enterprise", ent, "admin") != frappe.session.user:
				raise frappe.PermissionError

	doc.has_permission('read')

	context.doc = doc
