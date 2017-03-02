# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _


def is_enterprise_admin(user, enterprise):
	return frappe.db.get_value("IOT Enterprise", {"name": enterprise, "admin": user}, "admin")


def get_context(context):
	# if frappe.form_dict.new:

	name = frappe.form_dict.user or frappe.form_dict.name
	if not name:
		frappe.local.flags.redirect_location = "/me"
		raise frappe.Redirect

	user_roles = frappe.get_roles(frappe.session.user)
	if 'IOT User' not in user_roles or frappe.session.user == 'Guest':
		raise frappe.PermissionError("Your account is not an IOT User!")
		
	context.no_cache = 1
	context.show_sidebar = True
	# Get target user document object
	doc = frappe.get_doc('IOT User', name)
	# Check for Enterprise permission
	if not is_enterprise_admin(frappe.session.user, doc.get("enterprise")):
		raise frappe.PermissionError("Your account is not enterprise admin!")

	doc.has_permission('read')

	context.parents = [{"label": _("Back"), "route": frappe.get_request_header("referer")}]
	context.user_doc = frappe.get_doc("User", doc.user)
	context.doc = doc
