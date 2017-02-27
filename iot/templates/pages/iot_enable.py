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
	if 'IOT User' in user_roles:
		frappe.local.flags.redirect_location = "/iot_me"
		raise frappe.Redirect
		
	context.no_cache = 1
	context.show_sidebar = True

	def_ent = frappe.db.get_single_value("IOT Settings", "default_enterprise")

	doc = frappe.get_doc({"doctype": "IOT User", "enabled": True, "user": frappe.session.user, "enterprise": def_ent})
	# doc.insert()

	context.doc = doc