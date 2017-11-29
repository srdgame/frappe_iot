# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import format_datetime

class IOTDeviceError(Document):
	def on_submit(self):
		self.wechat_msg_send()

	def wechat_msg_send(self):
		if self.wechat_notify == 1 or self.wechat_notify == '1':
			frappe.enqueue('iot.iot.doctype.iot_device_error.iot_device_error.wechat_notify_by_name',
							err_name=self.name, err_doc=self)

	def wechat_tmsg_data(self):
		return {
			"first": {
				"value": _("Has new device alarm"),
				"color": "red"
			},
			"keyword1": {
				"value": self.error_type,
				"color": "blue"
			},
			"keyword2": {
				"value": frappe.get_value("IOT Device", self.device, "dev_name"),
				"color": "blue"
			},
			"keyword3": {
				"value": format_datetime(self.modified),
				"color": "green",
			},
			"remark": {
				"value": self.error_info
			}
		}

	def wechat_tmsg_url(self):
		#return "/view-iot-device-error?name=" + self.name
		return self.get_url()


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


