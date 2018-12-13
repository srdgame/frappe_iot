# -*- coding: utf-8 -*-
# Copyright (c) 2018, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def on_device_add(doc, method, company, owner_type, owner_id):
	frappe.enqueue('iot.iot_hub.doctype.iot_user_application.iot_user_application.handle_device_add',
		hooks_doc=doc, hooks_company=company, hooks_owner_type=owner_type, hooks_owner_id=owner_id)


def on_device_del(doc, method, company, owner_type, owner_id):
	frappe.enqueue('iot.iot_hub.doctype.iot_user_application.iot_user_application.handle_device_del',
		hooks_doc=doc, hooks_company=company, hooks_owner_type=owner_type, hooks_owner_id=owner_id)


def on_device_status(doc, method):
	frappe.enqueue('iot.iot_hub.doctype.iot_user_application.iot_user_application.handle_device_status',
		hooks_doc=doc, hooks_method=method)
