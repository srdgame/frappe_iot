# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from iot.iot.doctype.iot_user.iot_user import add_user, delete_user


def is_enterprise_admin(user, enterprise):
	return frappe.db.get_value("IOT Enterprise", {"name": enterprise, "admin": user}, "admin")


def get_context(context):
	user = frappe.session.user
	enterprise = frappe.form_dict.enterprise or frappe.db.get_value("IOT Enterprise", {"admin": user})
	delete_user(frappe.form_dict.name)

	frappe.local.flags.redirect_location = "/iot_enterprises/" + enterprise
	raise frappe.Redirect
