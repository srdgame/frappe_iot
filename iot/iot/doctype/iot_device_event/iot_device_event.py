# -*- coding: utf-8 -*-
# Copyright (c) 2018, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, throw
from frappe.model.document import Document
from frappe.utils.data import format_datetime


class IOTDeviceEvent(Document):
	def on_submit(self):
		frappe.enqueue_doc('IOT Device Event', self.name, 'wechat_msg_send')

	def wechat_msg_send(self):
		from cloud.cloud.doctype.cloud_company.cloud_company import get_wechat_app

		dev = frappe.get_doc("IOT Device", self.device)
		user_list = dev.find_owners(dev.owner_type, dev.owner_id)

		if len(user_list) > 0:
			app = get_wechat_app(dev.company)
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

