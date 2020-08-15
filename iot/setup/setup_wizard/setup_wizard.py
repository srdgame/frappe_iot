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
	frappe.logger(__name__).error("IOT Setup Wizard Args:{0}".format(json.dumps(args)))
	if frappe.get_value('User', args.hdb_user) is None:
		hdb_user = dict(doctype='User', email=args.hdb_user, first_name='HDB User', send_welcome_email=0, enabled=1)
		frappe.get_doc(hdb_user).insert(ignore_permissions=True)

	frappe.set_value("IOT HDB Settings", "IOT HDB Settings", "authorization_code", args.hdb_authorization_code)
	frappe.set_value("IOT HDB Settings", "IOT HDB Settings", "on_behalf", args.hdb_user)
	frappe.set_value("IOT HDB Settings", "IOT HDB Settings", "redis_server", args.hdb_redis_server)
	frappe.set_value("IOT HDB Settings", "IOT HDB Settings", "influxdb_server", args.hdb_influxdb_server)
	frappe.set_value("IOT HDB Settings", "IOT HDB Settings", "mqtt_root_password", args.hdb_mqtt_root_password)
	frappe.set_value("IOT HDB Settings", "IOT HDB Settings", "mqtt_device_password_sid", args.hdb_mqtt_device_password_sid)


# Only for programmatical use
def setup_complete(args=None):
	setup_hdb_settings(args)
