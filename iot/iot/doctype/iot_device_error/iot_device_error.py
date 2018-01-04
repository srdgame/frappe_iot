# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import format_datetime
from iot.iot.doctype.iot_device_error_rule.iot_device_error_rule import wechat_notify_check


class IOTDeviceError(Document):
	def on_submit(self):
		self.wechat_msg_send()

	def after_insert(self):
		wechat_notify_check(self)

	def wechat_msg_send(self):
		if self.wechat_notify == 1:
			frappe.enqueue('iot.iot.doctype.iot_device_error.iot_device_error.wechat_notify_by_name',
							err_name=self.name, err_doc=self)

	def wechat_tmsg_data(self):
		remark = _("Key: {0}").format(self.error_key) + "\n" + _("Info: {0}").format(self.error_info)
		return {
			"first": {
				"value": _("Has new device alarm"),
				"color": "#800000"
			},
			"keyword1": {
				"value": frappe.get_value("IOT Error Type", self.error_type, "description"),
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
		#return self.get_url()
		return "/iot_event_info?eventid=" + self.name


def wechat_notify_by_name(err_name, err_doc=None):
	from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_users
	from cloud.cloud.doctype.cloud_company.cloud_company import get_wechat_app

	err_doc = err_doc or frappe.get_doc("IOT Device Error", err_name)

	if err_doc.status in ["New", "Open"]:
		user_list = []
		bunch = frappe.db.get_value("IOT Device", err_doc.device, "bunch")
		if bunch is None:
			print("No user binded")
			return

		bunch_doc = frappe.get_doc("IOT Device Bunch", bunch)
		if bunch_doc.owner_type == "Cloud Company Group":
			print("Cloud Company Group", bunch_doc.owner_id)
			user_list = [d.name for d in list_users(bunch_doc.owner_id)]
		else:
			user_list.append(bunch_doc.owner_id)

		if len(user_list) > 0:
			app = get_wechat_app(bunch_doc.get_company())
			if app:
				from wechat.api import send_doc
				send_doc(app, 'IOT Device Error', err_doc.name, user_list)


