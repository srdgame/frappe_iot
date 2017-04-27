# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
import redis
from frappe import _
from iot.iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings


def get_context(context):
	name = frappe.form_dict.device or frappe.form_dict.name
	if not name:
		frappe.local.flags.redirect_location = "/me"
		raise frappe.Redirect

	user_roles = frappe.get_roles(frappe.session.user)
	if 'IOT User' not in user_roles or frappe.session.user == 'Guest':
		raise frappe.PermissionError
		
	context.no_cache = 1
	context.show_sidebar = True
	device = frappe.get_doc('IOT Device', name)

	device.has_permission('read')

	context.parents = [{"title": _("IOT Devices"), "route": "/iot_devices"}]
	context.doc = device
	context.parents = [
		{"title": _("Back"), "route": frappe.get_request_header("referer")},
		{"title": _("IOT Devices"), "route": "/iot_devices"}
	]

	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/1")
	context.devices = []
	for d in client.lrange(name, 0, -1):
		dev = {
			'sn': d
		}
		if d[0:len(name)] == name:
			dev['name']= d[len(name):]

		context.devices.append(dev)
