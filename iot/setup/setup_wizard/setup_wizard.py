# -*- coding: utf-8 -*-
# Copyright (c) 2020, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
import json
from frappe import _


def get_setup_stages(args=None):
	stages = [
		{
			'status': _('Setting up IOT HDB Settings'),
			'fail_msg': _('Failed to setup IOT HDB Settings'),
			'tasks': [
				{
					'fn': setup_hdb_settings,
					'args': args,
					'fail_msg': _('Failed to setup IOT HDB Settings'),
				}
			]
		}
	]

	return stages


def setup_hdb_settings(args):
	if frappe.get_value('User', args.hdb_user) is None:
		hdb_user = dict(doctype='User', email=args.hdb_user, first_name='HDB User', send_welcome_email=0, enabled=1)
		doc = frappe.get_doc(hdb_user).insert(ignore_permissions=True)
		doc.append_roles("Cloud Manager", "IOT Manager", "Wechat Manager")
		doc.save()
	if frappe.get_value('IOT User Api', args.hdb_user) is None:
		user_api = dict(doctype='IOT User Api', user=args.hdb_user, authorization_code=args.hdb_authorization_code)
		frappe.get_doc(user_api).insert(ignore_permissions=True)

	settings = frappe.get_doc("IOT HDB Settings")
	settings.set("authorization_code", args.hdb_authorization_code)
	settings.set("on_behalf", args.hdb_user)
	settings.set("redis_server", args.hdb_redis_server)
	settings.set("influxdb_server", args.hdb_influxdb_server)
	settings.set("mqtt_root_password", args.hdb_mqtt_root_password)
	settings.set("mqtt_device_password_sid", args.hdb_mqtt_device_password_sid)
	settings.save()


# Only for programmatical use
def setup_complete(args=None):
	setup_hdb_settings(args)
