# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _


def get_user_bunch_codes(user):
	return frappe.get_all("IOT Device Bunch",
						  filters={"owner_type" : "User", "owner_id": user},
						  fields=["name", "bunch_name", "code", "modified", "creation"])


def get_context(context):
	from cloud.cloud.doctype.cloud_company.cloud_company import list_user_companies
	from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups

	if frappe.session.user == 'Guest':
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect

	user_roles = frappe.get_roles(frappe.session.user)
	if 'IOT User' not in user_roles:
		raise frappe.PermissionError("Your account is not an IOT User! Please concat admin for user permission request!")

	context.no_cache = 1
	context.show_sidebar = True

	# context.parents = [{"title": _("Back"), "route": frappe.get_request_header("referer")}]

	context.doc = {
		"companies": list_user_companies(frappe.session.user),
		"groups": list_user_groups(frappe.session.user),
		"bunch_codes": get_user_bunch_codes(frappe.session.user)
	}
