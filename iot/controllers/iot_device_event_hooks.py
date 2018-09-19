# -*- coding: utf-8 -*-
# Copyright (c) 2018, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def after_insert(doc, method):
	frappe.enqueue('iot.iot_hub.doctype.iot_user_application.iot_user_application.handle_device_event_hooks',
				   hooks_doc=doc, hooks_method=method)

