# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class IOTDeviceErrorRule(Document):
	pass


def wechat_notify_check(err_doc):
	dev = frappe.get_doc("IOT Device", err_doc.device)
	if dev.owner_type == "User":
		if err_doc.wechat_notify == 1:
			err_doc.submit()
	else:
		rule = frappe.get_doc("IOT Device Error Rule", filter={"group":dev.owner_id, "error_type": err_doc.error_type})
		if rule:
			if err_doc.error_level >= rule.level:
				err_doc.submit()
