# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document


class IOTDeviceBunch(Document):
	def has_website_permission(self, ptype, verbose=False):
		"""Returns true if current user is the session user"""
		return self.owner_type == "User" and self.owner_id == frappe.session.user



@frappe.whitelist()
def add_bunch_code(code=None, name=None, owner_type=None, owner_id=None):
	"""
	Add device bunch code
	:param name: Bunch code name
	:param code: Bunch code
	:param type: Bunch code owner type
	:param id: Bunch code owner id
	:return: bunch code document
	"""
	if not frappe.request.method == "POST":
		raise frappe.ValidationError

	if 'IOT User' not in frappe.get_roles(frappe.session.user):
		raise frappe.PermissionError

	# Set proper owner_type owner_id to user
	if type is None or id is None:
		owner_type = "User"
		owner_id = frappe.session.user

	frappe.logger(__name__).info(_("Add bunch code {0} to {1}:{2}").format(code, owner_type, owner_id))

	if frappe.get_value("IOT Device Bunch", {"code": code}):
		return {"result": False, "data": "Bunch code already exists!"}


	doc = frappe.get_doc({
		"doctype": "IOT Device Bunch",
		"bunch_name": name,
		"code": code,
		"owner_type": owner_type,
		"owner_id": owner_id,
	})
	doc.insert()
	return doc


@frappe.whitelist()
def update_bunch_code_name(code=None, name=None):
	if not frappe.request.method == "POST":
		raise frappe.ValidationError

	if 'IOT User' not in frappe.get_roles(frappe.session.user):
		raise frappe.PermissionError

	frappe.logger(__name__).info(_("Update device bunch code {0} name to {1}").format(code, name))

	doc = frappe.get_doc('IOT Device Bunch', {"code": code})
	doc.set("bunch_name", name)
	doc.save()

	return doc

