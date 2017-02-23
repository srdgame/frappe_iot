# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw, msgprint, _
from frappe.model.document import Document


def valid_auth_code(auth_code=None):
	auth_code = auth_code or frappe.get_request_header("HDB_AuthorizationCode")
	if not auth_code:
		throw(_("HDB_AuthorizationCode is required in your HTTP Header!"))
	frappe.log(_("HDB_AuthorizationCode as {0}").format(auth_code))

	code = frappe.db.get_single_value("IOT HDB Settings", "authorization_code")
	if auth_code != code:
		throw(_("Authorization Code is incorrect!"))


@frappe.whitelist(allow_guest=True)
def login(usr=None, pwd=None):
	"""
	HDB Application checking for user login
	:param usr: Username (<Login Name>@<IOT Enterprise Domain>)
	:param pwd: Password (ERPNext User Password)
	:return: {"usr": <ERPNext user name>, "ent": <IOT Enterprise>}
	"""
	valid_auth_code()
	if not (usr and pwd):
		usr, pwd = frappe.form_dict.get('usr'), frappe.form_dict.get('pwd')
	frappe.log(_("HDB Checking login {0} password {1}").format(usr, pwd))

	if '@' not in usr:
		throw(_("Username must be <login_name>@<enterprise domain>"))

	login_name, domain = usr.split('@')
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
def list_devices(user=None):
	"""
	List devices according to user specified in query params by naming as 'usr'
		this user is ERPNext user which you got from @iot.auth.login
	:param authorization_code: IOT HDB Authorization Code
	:param user: ERPNext username
	:return: device list
	"""
	valid_auth_code()
	user = user or frappe.form_dict.get('user')
	if not user:
		throw(_("Query string user does not specified"))
	frappe.log(_("List Devices for user {0}").format(user))

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
	if frappe.request and frappe.request.method == "POST":
		return frappe.form_dict.get("text") or "No Text"
	return 'pong'


