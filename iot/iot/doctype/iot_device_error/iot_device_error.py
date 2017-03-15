# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from iot.iot.doctype.iot_settings.iot_settings import IOTSettings

class IOTDeviceError(Document):
	def on_update(self):
		if self.wechat_notify == 1 and self.wechat_sent != 1:
			frappe.enqueue('iot.iot.doctype.iot_device_error.iot_device_error.wechat_notify_by_name',
							err_name = self.name, err_doc=self)



def wechat_notify_by_name(err_name, err_doc=None):
	err_doc = err_doc or frappe.get_doc("Repair Issue", err_name)
	if err_doc.wechat_sent == 1:
		return

	if err_doc.status in ["New", "Open"]:
		user_list = {}
		bunch = frappe.db.get_value("IOT Device", err_doc.device, "bunch")
		if bunch is None:
			print("No user binded")
			return

		enterprise = None
		bunch_doc = frappe.get_doc("IOT Device Bunch", bunch)
		if bunch_doc.owner_type == "IOT Employee Group":
			user_list = [d[0] for d in frappe.db.get_values("IOT UserGroup", {"group": bunch_doc.owner_id}, "parent")]
		else:
			user_list.append(bunch_doc.owner_id)

		if user_list.count() > 0:
			enterprise = enterprise or frappe.get_value("IOT User", user_list[0], "enterprise") or IOTSettings.get_default_enterprise()

			app = frappe.get_value("IOT Enterprise", enterprise, "wechat_app")
			if app:
				from wechat.api import send_device_alarm
				alarm = {
					"title": _("有新的{0}").format(err_doc.error_type),
					"url": "/view-iot-device-error?name=" + err_doc.name,
					"name": frappe.get_value("IOT Device", err_doc.device, "dev_name"),
					"time": err_doc.modified,
					"content": err_doc.error_info,
					"remark": ""
				}
				send_device_alarm(app, user_list, alarm)

	# update flag
	err_doc.db_set("wechat_sent", 1)


def wechat_notify():
	"""Sends WeChat notifications if there are un-notified issues
		and `wechat_sent` is set as true."""

	for err in frappe.get_all("IOT Device Error", "name", filters={"wechat_notify": 1, "wechat_sent": 0}):
		wechat_notify_by_name(err.name)

