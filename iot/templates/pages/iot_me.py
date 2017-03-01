# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json


def get_user_bunch_codes(user):
	return frappe.get_all("IOT Device Bunch",
						  filters={"owner_type" : "User", "owner_id": user},
						  fields=["name", "bunch_name", "code", "modified", "creation"])


def get_context(context):
	if frappe.session.user == 'Guest':
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect

	user_roles = frappe.get_roles(frappe.session.user)
	if 'IOT User' not in user_roles:
		raise frappe.PermissionError("Your account is not an IOT User! Please concat admin for user permission request!")

	context.no_cache = 1
	context.show_sidebar = True

	codes = get_user_bunch_codes(frappe.session.user)
	context.codes = codes

	context.parents = [{"label": _("Back"), "route": frappe.get_request_header("referer")}]

	if frappe.get_value("IOT User", frappe.session.user):
		doc = frappe.get_doc('IOT User', frappe.session.user)
		doc.has_permission('read')

		context.doc = doc
	else:
		context.doc = {
			"name": frappe.session.user,
			"user": frappe.session.user,
			"enterprise": "Public",
		}
