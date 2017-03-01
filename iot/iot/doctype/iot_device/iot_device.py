# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import traceback
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, cstr


class IOTDevice(Document):
	def update_status(self, status):
		""" update device status """
		self.set("device_status", status)
		self.set("last_updated", now())
		self.save()

	def update_bunch(self, bunch):
		""" update device bunch code """
		self.set("bunch", bunch)
		self.set("last_updated", now())
		self.save()

	@staticmethod
	def check_sn_exists(sn):
		return frappe.db.get_value("IOT Device", {"sn": sn}, "sn")

	@staticmethod
	def list_device_sn_by_bunch(bunch):
		return [d[0] for d in frappe.db.get_values("IOT Device", {"bunch": bunch}, "sn")]

	@staticmethod
	def get_device_doc(sn):
		dev = None
		try:
			dev = frappe.get_doc("IOT Device", sn)
		except Exception, e:
			frappe.logger(__name__).error(e)
			traceback.print_exc()
		finally:
			frappe.logger(__name__).error(_("Device {0} does not exits!").format(sn))
		return dev

	@staticmethod
	def find_owners_by_bunch(bunch):
		if not bunch:
			return []
		code = frappe.get_doc("IOT Device Bunch", bunch)

		id = code.get("owner_id")
		if code.get("owner_type") == "User":
			return [id]

		if code.get("owner_type") == "IOT Employee Group":
			return frappe.db.get_values("IOT UserGroup", {"group": id}, "parent")

		raise Exception("You should got here!")

	def has_website_permission(self, ptype, verbose=False):
		user = frappe.session.user
		if self.owner_type == "User" and self.owner_id == user:
			return True

		groups = [d[0] for d in frappe.db.get_values('IOT UserGroup', {"parent": user}, "group")]
		if self.owner_type == "IOT Employee Group" and self.owner_id in groups:
			return True

		return False


def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	groups = [d[0] for d in frappe.db.get_values('IOT UserGroup', {"parent": user}, "group")]

	return """(`tabIOT Device Bunch`.owner_type='User' and `tabIOT Device Bunch`.owner_id='%(user)s'
		or (`tabIOT Device Bunch`.owner_type='IOT Employee Group' and
			`tabIOT Device Bunch`.owner_id in ('%(groups)s'))
		""" % {
			"user": frappe.db.escape(user),
			"groups": "', '".join([frappe.db.escape(r) for r in groups])
		}


def has_permission(doc, user):
	if not user: user = frappe.session.user
	if doc.owner_type=="User" and doc.owner_id==user:
		return True

	groups = [d[0] for d in frappe.db.get_values('IOT UserGroup', {"parent": user}, "group")]
	if doc.owner_type == "IOT Employee Group" and doc.owner_id in groups:
		return True

	return False


def get_device_list(doctype, txt, filters, limit_start, limit_page_length=20, order_by="modified desc"):
	return frappe.db.sql('''select distinct device.*
		from `tabIOT Device` device, `tabIOT UserGroup` user_group, `tabIOT Device Bunch` bunch_code 
		where
			(bunch_code.owner_type = "User"
			and bunch_code.owner_id = %(user)s
			and bunch_code.code = device.bunch)
			or (bunch_code.owner_type = "IOT Employee Group"
			and user_group.group = bunch_code.owner_id
			and user_group.parent = %(user)s
			and bunch_code.code = device.bunch)
			order by device.{0}
			limit {1}, {2}
		'''.format(order_by, limit_start, limit_page_length),
			{'user':frappe.session.user},
			as_dict=True,
			update={'doctype':'IOT Device'})


def get_list_context(context=None):
	return {
		"show_sidebar": True,
		"show_search": True,
		"no_breadcrumbs": True,
		"title": _("IOT Devices"),
		"introduction": _('IOT Devices of your group/account'),
		"get_list": get_device_list,
		"row_template": "templates/generators/iot_device_row.html",
	}
