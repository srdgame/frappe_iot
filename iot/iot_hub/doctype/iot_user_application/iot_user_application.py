# -*- coding: utf-8 -*-
# Copyright (c) 2018, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests
from frappe import throw, _, _dict
from frappe.model.document import Document
from iot.iot.doctype.iot_device.iot_device import has_permission_inter


class IOTUserApplication(Document):
	def validate(self):
		if not self.on_behalf:
			self.on_behalf = frappe.session.user

		if not "System Manager" in frappe.get_roles():
			if self.on_behalf != frappe.session.user:
				throw(_("Invalid onbehalf user!"))

		if self.on_behalf == 'Administrator':
			throw(_("User application cannot bind to Administrator!"))


app_props = ["name","app_name","description","uri","on_behalf","device","device_data","device_event",
			"device_data_mqtt_host","device_data_mqtt_user","device_data_mqtt_passwd","modified"]


def _list_user_apps(user=None):
	if 'IOT Manager' not in frappe.get_roles():
		return []

	if user:
		return frappe.get_all("IOT User Application", fields=app_props, filters={"on_behalf": user, "enabled": 1})
	return frappe.get_all("IOT User Application", fields=app_props, filters={"enabled": 1})


def list_user_apps(user=None):
	apps = _list_user_apps(user)
	for app in apps:
		app['auth_code'] = frappe.get_value("IOT User Api", app.on_behalf, "authorization_code")
	return apps


def init_request_headers(headers, code):
	headers['Accept'] = 'application/json'
	headers['AuthorizationCode'] = code


def fire_hooks_request(name, uri, data):
	session = requests.session()
	init_request_headers(session.headers, name)
	r = session.post(uri, json=data)


def fire_device_event_hooks(name, uri, doc):
	from iot.iot.doctype.iot_device_event.iot_device_event import event_fields
	data = _dict({})
	for field in event_fields:
		data[field] = doc.get(field)
	return fire_hooks_request(name, uri + "/device_event", data)


def fire_device_owner_hooks(name, uri, sn, op, company):
	return fire_hooks_request(name, uri + "/device", {
		"sn": sn,
		"op": op,
		"company": company
	})


def fire_device_status(name, uri, doc):
	return fire_hooks_request(name, uri + "/device_status", {
		"sn": doc.sn,
		"status": doc.device_status,
		"time": doc.last_updated
	})


def handle_device_event_hooks(hooks_doc, hooks_method):
	dev = frappe.get_doc("IOT Device", hooks_doc.device)
	apps = frappe.get_all("IOT User Application", fields=["name", "on_behalf", "uri"], filters={"device_event": 1, 'enabled': 1})
	for app in apps:
		if has_permission_inter(app.on_behalf, dev.name):
			fire_device_event_hooks(app.name, app.uri, hooks_doc)


def handle_device_add(hooks_doc, hooks_company, hooks_owner_type, hooks_owner_id):
	apps = frappe.get_all("IOT User Application", fields=["name", "on_behalf", "uri"], filters={"device": 1, 'enabled': 1})
	for app in apps:
		if has_permission_inter(app.on_behalf, hooks_doc.name, hooks_company, hooks_owner_type, hooks_owner_id):
			fire_device_owner_hooks(app.name, app.uri, hooks_doc.name, 'add', hooks_company)


def handle_device_del(hooks_doc, hooks_company, hooks_owner_type, hooks_owner_id):
	apps = frappe.get_all("IOT User Application", fields=["name", "on_behalf", "uri"], filters={"device": 1, 'enabled': 1})
	for app in apps:
		if has_permission_inter(app.on_behalf, hooks_doc.name, hooks_company, hooks_owner_type, hooks_owner_id):
			fire_device_owner_hooks(app.name, app.uri, hooks_doc.name, 'del', hooks_company)


def handle_device_status(hooks_doc, hooks_method):
	apps = frappe.get_all("IOT User Application", fields=["name", "on_behalf", "uri"], filters={"device": 1, 'enabled': 1})
	for app in apps:
		if has_permission_inter(app.on_behalf, hooks_doc.name):
			fire_device_status(app.name, app.uri, hooks_doc)
