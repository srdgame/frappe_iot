# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw, msgprint, _
from frappe.model.document import Document


def valid_client():
	auth_code = frappe.form_dict.get('authorization_code')
	if not auth_code:
		throw(_("Authorization Code is required!"))
	code = frappe.db.get_single_value("IOT HDB Settings", "authorization_code")
	if auth_code != code:
		throw(_("Authorization Code is incorrect!"))


@frappe.whitelist(allow_guest=True)
def login(arg=None):
	valid_client()
	hdb_user, pwd = frappe.form_dict.get('usr'), frappe.form_dict.get('pwd')
	if '@' not in hdb_user:
		throw(_("Username must be <login_name>@<enterprise domain>"))

	login_name, domain = hdb_user.split('@')
	enterprise = frappe.db.get_value("IOT Enterprise", {"domain": domain}, "name")
	if not enterprise:
		throw(_("Enterprise Domain {0} does not exists").format(domain))

	user = frappe.db.get_value("IOT User", {"enterprise": enterprise, "login_name": login_name}, "user")
	if not user:
		throw(_("User login_name {0} not found in Enterprise {1}").format(login_name, enterprise))

	frappe.local.login_manager.authenticate(user, pwd)
	if frappe.local.login_manager.user != user:
		throw(_("Username password is not matched!"))
	
	return {"usr": user, "ent": enterprise}


@frappe.whitelist(allow_guest=True)
def list_devices(arg=None):
	"""
	List devices according to user specified in query params by naming as 'usr'
		this user is ERPNext user which you got from @iot.auth.login
	:param arg: None
	:return: device list
	"""
	valid_client()
	user = frappe.form_dict.get('usr')
	user_doc = frappe.get_doc("IOT User", user)
	groups = user_doc.get("group_assigned")
	print(groups)
	devices = []
	for g in groups:
		bunch_codes = [d[0] for d in frappe.db.get_values("IOT Device Bunch", {"group": g.group}, "code")]
		sn_list = []
		for c in bunch_codes:
			sl = frappe.db.get_values("IOT Device", {"bunch": c}, "sn")
			sn_list.append({"bunch": c, "sn": [d[0] for d in sl]})
		devices.append({"group": g.group, "devices": sn_list})

	return devices

@frappe.whitelist(allow_guest=True)
def ping():
	return 'pong'


