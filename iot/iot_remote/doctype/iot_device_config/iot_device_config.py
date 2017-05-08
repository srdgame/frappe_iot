# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class IOTDeviceConfig(Document):
	pass


def query_device(doctype, txt, searchfield, start, page_len, filters):

	group = filters.get("group")
	if not group:
		return ""

	codes = [d[0] for d in frappe.db.get_values("IOT Device Bunch", {"owner_type": "Cloud Company Group", "owner_id": group}, "code")]
	if len(codes) == 0:
		return ""

	return frappe.db.sql("""select name, dev_name from `tabIOT Device`
		where bunch in %s
		and %s like %s order by name limit %s, %s""" %
		("('"+"','".join(codes)+"')", searchfield, "%s", "%s", "%s"),
		("%%%s%%" % txt, start, page_len), as_list=1)
