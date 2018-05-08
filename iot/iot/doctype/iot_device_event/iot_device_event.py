# -*- coding: utf-8 -*-
# Copyright (c) 2018, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, throw
from frappe.model.document import Document
from frappe.utils.data import format_datetime
from cloud.cloud.doctype.cloud_company.cloud_company import get_wechat_app
from iot.iot.doctype.iot_device.iot_device import IOTDevice


class IOTDeviceEvent(Document):
	def after_insert(self):
		if self.wechat_notify == 1 and get_wechat_app(self.owner_company):
			self.submit()

	def on_submit(self):
		if self.wechat_notify == 1:
			frappe.enqueue_doc('IOT Device Event', self.name, 'wechat_msg_send')

	def wechat_msg_send(self):
		user_list = IOTDevice.find_owners(self.owner_type, self.owner_id)

		if len(user_list) > 0:
			app = get_wechat_app(self.owner_company)
			if app:
				from wechat.api import send_doc
				send_doc(app, 'IOT Device Event', self.name, user_list)

	def wechat_tmsg_data(self):
		remark = _("Level: {0}\nInfo: {1}\nData:{2}").format(self.event_level, self.event_info, self.event_data)
		return {
			"first": {
				"value": _("Has new device alarm"),
				"color": "#800000"
			},
			"keyword1": {
				"value": self.event_type,
				"color": "#000080"
			},
			"keyword2": {
				"value": frappe.get_value("IOT Device", self.device, "dev_name"),
				"color": "#000080"
			},
			"keyword3": {
				"value": format_datetime(self.modified),
				"color": "#008000",
			},
			"remark": {
				"value": remark
			}
		}

	def wechat_tmsg_url(self):
		return self.get_url()


def on_doctype_update():
	"""Add indexes in `IOT Device Event`"""
	frappe.db.add_index("IOT Device Event", ["device", "owner_company"])
	frappe.db.add_index("IOT Device Event", ["owner_type", "owner_id"])


def has_permission(doc, ptype, user):
	if 'IOT Manager' in frappe.get_roles(user):
		return True

	company = frappe.get_value('IOT Device Event', doc.name, 'company')
	if frappe.get_value('Cloud Company', {'admin': user, 'name': company}):
		return True

	owner_type = frappe.get_value('IOT Device Event', doc.name, 'owner_type')
	owner_id = frappe.get_value('IOT Device Event', doc.name, 'owner_id')

	if owner_type == 'User' and owner_id == user:
		return True

	if owner_type == "Cloud Company Group":
		from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_users
		for d in list_users(owner_id):
			if d.name == user:
				return True

	if owner_type == '' and owner_id == None:
		return True

	return False