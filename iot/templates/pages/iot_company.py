# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from six.moves.urllib.parse import urlencode


def get_context(context):
	name = frappe.form_dict.company or frappe.form_dict.name
	#frappe.local.flags.redirect_location = "/cloud_company?name=" + quote(name.encode('utf-8')) + "&group_hack_url=iot_company_groups"
	frappe.local.flags.redirect_location = "/cloud_company?" + urlencode({
		"name": name.encode('utf-8'),
		"group_hack_url": "iot_company_groups"
	})
	raise frappe.Redirect
