# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class IOTDeviceErrorRule(Document):
	pass


def wechat_notify_check(err_doc):
	if err_doc.wechat_notify == 0:
		return
	dev = frappe.get_doc("IOT Device", err_doc.device)
	bunch = frappe.get_doc("IOT Device Bunch", dev.bunch)
	if bunch.owner_type == "User":
		err_doc.submit()
	else:
		rules = frappe.get_all("IOT Device Error Rule", filters={"group":bunch.owner_id, "error_type": err_doc.error_type}, fields=["name", "level"])
		for rule in rules:
			if err_doc.error_level >= rule.level:
				err_doc.submit()
				return
