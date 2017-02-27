# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json


def get_context(context):
	user_roles = frappe.get_roles(frappe.session.user)
	if 'IOT User' not in user_roles or frappe.session.user == 'Guest':
		raise frappe.PermissionError("Your account is not an IOT User!")
		
	context.no_cache = 1
	context.show_sidebar = True
	doc = frappe.get_doc('IOT User', frappe.session.user)
	doc.has_permission('read')

	context.doc = doc
