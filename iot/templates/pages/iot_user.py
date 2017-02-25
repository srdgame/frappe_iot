# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json


def is_enterperise_admin(user, enterprise):
		return frappe.db.get_value("IOT Enterprise", {"name": enterprise, "admin": user}, "admin")


def get_context(context):
	if frappe.form_dict.new:

	name = frappe.form_dict.user or frappe.form_dict.name
	if not name:
		frappe.local.flags.redirect_location = "/me"
		raise frappe.ValidationError

	user_roles = frappe.get_roles(frappe.session.user)
	if 'IOT User' not in user_roles or frappe.session.user == 'Guest':
		raise frappe.PermissionError("Your are not an IOT User!")
		
	context.no_cache = 1
	context.show_sidebar = True
	doc = frappe.get_doc('IOT User', name)
	if not is_enterperise_admin(frappe.session.user, doc.get("enterprise")):
		raise frappe.PermissionError("Your are not enterprise admin!")

	doc.has_permission('read')

	context.doc = doc
