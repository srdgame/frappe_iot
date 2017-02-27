# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import requests
import json
from frappe import _


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

	def_ent = frappe.db.get_single_value("IOT Settings", "default_enterprise")

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


@frappe.whitelist(allow_guest=True)
def enable(enabled=None, user=None, enterprise=None, login_name=None):
	if not frappe.request.method == "POST":
		raise frappe.ValidationError

	if frappe.session.user != user:
		raise frappe.PermissionError

	frappe.logger(__name__).info(_("Enable IOT User for {0} login_name {1}").format(user, login_name))

	if enabled == "True":
		enabled = True
	frappe.session.user = frappe.db.get_single_value("IOT HDB Settings", "on_behalf") or "Administrator"
	doc = frappe.get_doc({
		"doctype": "IOT User",
		"enabled": enabled,
		"user": user,
		"enterprise": enterprise,
		"login_name": login_name
	})
	doc.insert()
	frappe.session.user = user

	return {"result": True, "data": doc}