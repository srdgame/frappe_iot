# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint


class IOTDeviceBunch(Document):
	def on_trash(self):
		# TODO:Let's verify devices.
		print("DO it!")


@frappe.whitelist()
def add_bunch_code(code=None, bunch_name=None, owner_type=None, owner_id=None):
	"""
	Add device bunch code
	:param bunch_name: Bunch code name
	:param code: Bunch code
	:param type: Bunch code owner type
	:param id: Bunch code owner id
	:return: bunch code document
	"""

	if 'IOT User' not in frappe.get_roles(frappe.session.user):
		frappe.throw(_("You are not an IOT User"))

	# Set proper owner_type owner_id to user
	if owner_type is None or owner_id is None:
		owner_type = "User"
		owner_id = frappe.session.user

	frappe.logger(__name__).info(_("Add bunch code {0} to {1}:{2}").format(code, owner_type, owner_id))

	if frappe.get_value("IOT Device Bunch", {"code": code}):
		frappe.throw(_("Bunch code already exists!"))

	doc = frappe.get_doc({
		"doctype": "IOT Device Bunch",
		"bunch_name": bunch_name,
		"code": code,
		"owner_type": owner_type,
		"owner_id": owner_id,
	})
	doc.insert()

	if owner_type == "User":
		return "/iot_me"
	else:
		return ("/iot_company_groups/{0}").format(owner_id)


@frappe.whitelist()
def update_bunch_code_name(code=None, bunch_name=None):
	if not frappe.request.method == "POST":
		raise frappe.ValidationError

	if 'IOT User' not in frappe.get_roles(frappe.session.user):
		raise frappe.PermissionError

	frappe.logger(__name__).info(_("Update device bunch code {0} name to {1}").format(code, bunch_name))

	doc = frappe.get_doc('IOT Device Bunch', {"code": code})
	doc.set("bunch_name", bunch_name)
	doc.save()

	return doc

