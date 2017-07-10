# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from cloud.templates.pages.cloud_company_group import get_context as cloud_get_context


def get_context(context):
	name = frappe.form_dict.group or frappe.form_dict.name

	cloud_get_context(context)

	context.parents = [{"title": context.doc.group_name, "route": "/iot_companies/" + context.doc.company}]
	#context.doc.bunch_codes = get_bunch_codes(name, start=0, search=frappe.form_dict.get("search"))


'''
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
'''
