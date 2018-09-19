# -*- coding: utf-8 -*-
# Copyright (c) 2018, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from iot.iot_hub.doctype.iot_user_application.iot_user_application import handle_device_add, handle_device_del, handle_device_status


def on_device_add(doc, method, company, owner_type, owner_id):
	handle_device_add(doc, company, owner_type, owner_id)


def on_device_del(doc, method, company, owner_type, owner_id):
	handle_device_del(doc, company, owner_type, owner_id)

def on_device_status(doc, method):
	handle_device_status(doc, method)
