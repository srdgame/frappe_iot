# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import requests
import json
from frappe import _
from iot.iot.doctype.iot_settings.iot_settings import IOTSettings


def get_context(context):
	if frappe.session.user == 'Guest':
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect

	user_roles = frappe.get_roles(frappe.session.user)
	if 'IOT User' not in user_roles:
		raise frappe.PermissionError("Your account is not an IOT User! Please concat admin for user permission request!")

	if frappe.get_value("IOT User", frappe.session.user, "name"):
		frappe.local.flags.redirect_location = "/iot_me"
		raise frappe.Redirect

	context.no_cache = 1
	context.show_sidebar = True

	def_ent = IOTSettings.get_default_enterprise()

	login_name, domain = frappe.session.user.split('@')
	doc = frappe.get_doc({
		"doctype": "IOT User",
		"enabled": True,
		"user": frappe.session.user,
		"enterprise": def_ent,
		"login_name": login_name
	})
	# doc.insert()

	context.doc = doc