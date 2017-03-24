# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from urllib import quote, urlencode


def get_context(context):
	name = frappe.form_dict.company or frappe.form_dict.name
	#frappe.local.flags.redirect_location = "/cloud_company?name=" + quote(name.encode('utf-8')) + "&group_hack_url=iot_company_groups"
	frappe.local.flags.redirect_location = "/cloud_company?" + urlencode({
		"name": name.encode('utf-8'),
		"group_hack_url": "iot_company_groups"
	})
	raise frappe.Redirect
