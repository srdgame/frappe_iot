# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw, msgprint, _
from frappe.model.document import Document

@frappe.whitelist()
def login(arg=None):
	hdb_user, pwd = frappe.form_dict.get('usr'), frappe.form_dict.get('pwd')
	login_name, domain = hdb_user.split('@')
	enterprise = frappe.get_value("IOT Enterprise", {"domain": domain}, "name")
	if not enterprise:
		throw(_("Enterprise Domain {0} does not exists").format(domain))

	user = frappe.get_value("IOT User", {"enterprise": enterprise, "login_name": login_name}, "user")
	if not user:
		throw(_("User login_name {0} not found in Enterprise {1}").format(login_name, enterprise))

	frappe.local.login_manager.authenticate(user, pwd)
	if frappe.local.login_manager.user == user:
		throw(_("Username password is not matched!"))

	return user

@frappe.whitelist(allow_guest=True)
def ping():
	return 'pong'


