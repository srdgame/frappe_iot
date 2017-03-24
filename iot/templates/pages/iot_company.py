# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from urllib import quote, urlencode
from frappe import _
from cloud.templates.pages.cloud_company import get_context as cloud_get_context

def get_context(context):
	name = frappe.form_dict.company or frappe.form_dict.name
	frappe.local.flags.redirect_location = "/cloud_company?name=" + urlencode(name) + "&group_hack_url=iot_company_groups"
	raise frappe.Redirect