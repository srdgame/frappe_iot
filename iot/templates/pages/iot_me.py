# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json


def get_context(context):
	if frappe.session.user == 'Guest':
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect

	user_roles = frappe.get_roles(frappe.session.user)
	if 'IOT User' not in user_roles:
		raise frappe.PermissionError("Your account is not an IOT User! Please concat admin for user permission request!")

	try:
		context.no_cache = 1
		context.show_sidebar = True
		doc = frappe.get_doc('IOT User', frappe.session.user)
		doc.has_permission('read')

		context.doc = doc
	except Exception:
		frappe.local.flags.redirect_location = "/iot_enable"
		raise frappe.Redirect
