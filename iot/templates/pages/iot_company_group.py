# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from cloud.cloud.doctype.cloud_company.cloud_company import list_admin_companies


def is_company_admin(user, company):
	return company in list_admin_companies(user)


def get_context(context):
	name = frappe.form_dict.group or frappe.form_dict.name
	if not name:
		frappe.local.flags.redirect_location = "/me"
		raise frappe.Redirect

	user_roles = frappe.get_roles(frappe.session.user)
	if 'IOT User' not in user_roles or frappe.session.user == 'Guest':
		raise frappe.PermissionError

	context.no_cache = 1
	context.show_sidebar = True
	doc = frappe.get_doc('Cloud Company Group', name)
	is_admin = is_company_admin(frappe.session.user, doc.company)

	doc.has_permission('read')

	if is_admin:
		doc.users = get_users(doc.name, start=0, search=frappe.form_dict.get("search"))
	doc.bunch_codes = get_bunch_codes(doc.name, start=0, search=frappe.form_dict.get("search"))

	context.parents = [{"label": doc.parent, "route": "/iot_companies/" + doc.company}]
	context.doc = doc
	"""
	context.parents = [
		{"label": _("Back"), "route": frappe.get_request_header("referer")},
		{"label": doc.parent, "route": "/iot_companies/" + doc.parent}
	]
	"""


def get_users(group, start=0, search=None):
	filters = {"parent": group}
	if search:
		filters["user"] = ("like", "%{0}%".format(search))

	user_names = frappe.get_all("Cloud Company GroupUser", filters=filters,
		fields=["user"],
		limit_start=start, limit_page_length=10)

	users = []
	for user in user_names:
		u = frappe.get_value("Cloud Employee", user.user, ["user", "modified", "creation"])
		users.append({
			"name": u[0],
			"modified": u[1],
			"creation": u[2]
		})

	return users


def get_bunch_codes(group, start=0, search=None):
	filters = {
		"owner_type": "Cloud Company Group",
		"owner_id": group
	}
	if search:
		filters["bunch_name"] = ("like", "%{0}%".format(search))

	bunch_codes = frappe.get_all("IOT Device Bunch", filters=filters,
		fields=["name", "bunch_name", "code", "modified", "creation"],
		limit_start=start, limit_page_length=10)


	return bunch_codes

