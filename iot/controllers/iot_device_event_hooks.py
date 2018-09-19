# -*- coding: utf-8 -*-
# Copyright (c) 2018, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from iot.iot_hub.doctype.iot_user_application.iot_user_application import handle_device_event_hooks


def after_insert(doc, method):
	handle_device_event_hooks(doc, method)

