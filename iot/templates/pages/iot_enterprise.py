# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from iot.iot.doctype.iot_settings.iot_settings import IOTSettings


def get_context(context):
	name = frappe.form_dict.enterprise or frappe.form_dict.name \
			or frappe.get_value("IOT User", frappe.session.user, "enterprise") \
			or IOTSettings.get_default_enterprise()

	if not name:
		frappe.local.flags.redirect_location = "/me"
		raise frappe.Redirect

	user_roles = frappe.get_roles(frappe.session.user)
	if 'IOT User' not in user_roles or frappe.session.user == 'Guest':
		raise frappe.PermissionError

	context.no_cache = 1
	context.show_sidebar = True

	enterprise = frappe.get_doc('IOT Enterprise', name)
	enterprise.has_permission('read')

	if enterprise.get('admin') == frappe.session.user:
		enterprise.users = get_users(enterprise.name, start=0, enabled=True, search=frappe.form_dict.get("search"))
		context.is_admin = True
	else:
		user_groups= [d[0] for d in frappe.db.get_values("IOT UserGroup", {"parent" : frappe.session.user}, "group")]
		enterprise.groups = [g for g in enterprise.groups if g.name in user_groups]

	# context.parents = [{"label": _("IOT Enterprises"), "route": "/iot_enterprises"}]

	context.doc = enterprise
	"""
	context.parents = [
		{"label": _("Back"), "route": frappe.get_request_header("referer")},
		{"label": _("IOT Enterprises"), "route": "/iot_enterprises"}
	]
	"""

def get_users(enterprise, start=0, search=None, enabled=None):
	filters = {"enterprise": enterprise}
	if search:
		filters["user"] = ("like", "%{0}%".format(search))
	if enabled:
		filters["enabled"] = enabled

	users = frappe.get_all("IOT User", filters=filters,
		fields=["name", "enabled", "modified", "creation"],
		limit_start=start, limit_page_length=10)

	return users
