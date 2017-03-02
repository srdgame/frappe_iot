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
	enterprise = frappe.form_dict.enterprise or frappe.db.get_value("IOT Enterprise", {"admin": frappe.session.user})

	user = frappe.form_dict.name
	if not user:
		raise frappe.ValidationError(_("IOT User name is required!"))

	info = _("IOT User {0} has been removed!").format(user)

	try:
		delete_user(user)
	except Exception, e:
		info = e

	context.no_cache = 1
	context.show_sidebar = True

	context.parents = [{"label": enterprise, "route": "/iot_enterprises/" + enterprise}]

	context.doc = {
		"enterprise": enterprise,
		"info": info
	}
