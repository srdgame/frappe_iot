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
	device = frappe.get_doc('IOT Device', name)

	device.has_permission('read')

	context.doc = device
	context.parents = [
		{"label": _("Back"), "route": frappe.get_request_header("referer")},
		{"label": _("IOT Devices"), "route": "/iot_devices"}
	]