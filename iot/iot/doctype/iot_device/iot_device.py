# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.website.website_generator import WebsiteGenerator
from frappe import _
from frappe.utils import now, get_datetime, cstr


class IOTDevice(WebsiteGenerator):
	website = frappe._dict(
		template="templates/generators/iot_device.html",
		condition_field="enabled",
		order_by="modified desc",
		page_title_field="dev_name",
	)

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
		finally:
			frappe.logger(__name__).error(_("Device {0} does not exits!").format(sn))
		return dev

	@staticmethod
	def find_owners_by_bunch(bunch):
		if not bunch:
			return []
		group = frappe.get_value("IOT Device Bunch", bunch, "group")
		return frappe.db.get_values("IOT UserGroup", {"group": group}, "parent")

	def get_context(self, context):
		context.parents = [{'name': 'iot_devices', 'title': _('All IOT Devices') }]


def get_device_list(doctype, txt, filters, limit_start, limit_page_length=20):
	return frappe.db.sql('''select *
		from `tabIOT Device`
		where
			admin = %(user)s
			order by modified desc
			limit {0}, {1}
		'''.format(limit_start, limit_page_length),
			{'user':frappe.session.user},
			as_dict=True,
			update={'doctype':'IOT Device'})


def get_list_context(context):
	context.title = _("IOT Devices")
	context.introduction = _('Your IOT Devices')
	context.get_list = get_device_list
	context.template = "templates/generators/iot_device.html"
