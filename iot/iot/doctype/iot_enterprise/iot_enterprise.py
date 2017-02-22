# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class IOTEnterprise(Document):
	pass


@frappe.whitelist()
def get_groups(enterprise):
	"""return all groups in specified enterprise"""
	groups = frappe.db.sql("""select name, grp_name, description
			from `tabIOT Employee Group`
			where parent = %(enterprise)s""", {"enterprise": enterprise}, as_dict=1)
	return groups

