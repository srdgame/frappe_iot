# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from iot.iot.doctype.iot_device_error_rule.iot_device_error_rule import wechat_notify_check

def after_insert(doc, method):
	wechat_notify_check(doc)
