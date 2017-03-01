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

	if not frappe.get_value("IOT User", frappe.session.user, "name"):
		frappe.local.flags.redirect_location = "/iot_me"
		raise frappe.PermissionError("Your account is not an IOT User!")

	user = frappe.form_dict.name
	if not user:
		frappe.local.flags.redirect_location = "/update-password"
		raise frappe.Redirect

	context.no_cache = 1
	context.show_sidebar = False

	ent = frappe.get_value("IOT User", frappe.session.user, "enterprise")
	if frappe.session.user != frappe.get_value("IOT Enterprise", ent, "admin"):
		raise frappe.PermissionError("Your account is not admin of {0}").format(ent)

	if ent != frappe.get_value("IOT User", user, "enterprise"):
		raise frappe.PermissionError("User {0} is in Enterprise {1}").format(user, ent)

	doc = frappe.get_doc("User", user)

	context.doc = doc