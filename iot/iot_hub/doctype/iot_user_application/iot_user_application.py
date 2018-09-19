# -*- coding: utf-8 -*-
# Copyright (c) 2018, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests
from frappe import throw, _
from frappe.model.document import Document
from iot.iot.doctype.iot_device.iot_device import has_permission_inter


app_props = ['name', 'desc', 'uri', 'on_behalf', 'device', 'device_data', 'device_event']


class IOTUserApplication(Document):
	def validate(self):
		if not self.on_behalf:
			self.on_behalf = frappe.session.user

		if not "System Manager" in frappe.get_roles():
			if self.on_behalf != frappe.session.user:
				throw(_("Invalid onbehalf user!"))

		if self.on_behalf == 'Administrator':
			throw(_("User application cannot bind to Administrator!"))


def list_user_apps(user=None):
	if user:
		return frappe.get_all("IOT User Application", {"on_behalf": user, 'enabled': 1}, fields=app_props)
	return frappe.get_all("IOT User Application", {'enabled': 1}, fields=app_props)


def init_request_headers(headers, code):
	headers['Accept'] = 'application/json'
	headers['AuthorizationCode'] = code


def fire_hooks_request(name, uri, data):
	session = requests.session()
	init_request_headers(session.headers, name)
	r = session.post(uri, json=data)


def fire_device_event_hooks(name, uri, doc):
	return fire_hooks_request(name, uri + "/device_event", doc.as_dict())


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


def handle_device_event_hooks(doc, method):
	dev = frappe.get_doc("IOT Device", doc.device)
	apps = frappe.get_all("IOT User Application", {"device_event": 1, 'enabled': 1}, fields=["name", "on_behalf", "uri"])
	for app in apps:
		if dev.has_permission("read", app.on_behalf):
			fire_device_event_hooks(doc, app.name, app.uri)


def handle_device_add(doc, company, owner_type, owner_id):
	apps = frappe.get_all("IOT User Application", {"device": 1, 'enabled': 1}, fields=["name", "on_behalf", "uri"])
	for app in apps:
		if has_permission_inter(app.on_behalf, doc.name, company, owner_type, owner_id):
			fire_device_owner_hooks(app.name, app.uri, doc, 'add', company)


def handle_device_del(doc, company, owner_type, owner_id):
	apps = frappe.get_all("IOT User Application", {"device": 1, 'enabled': 1}, fields=["name", "on_behalf", "uri"])
	for app in apps:
		if has_permission_inter(app.on_behalf, doc.name, company, owner_type, owner_id):
			fire_device_owner_hooks(app.name, app.uri, doc, 'del', company)


def handle_device_status(doc, method):
	apps = frappe.get_all("IOT User Application", {"device": 1, 'enabled': 1}, fields=["name", "on_behalf", "uri"])
	for app in apps:
		if has_permission_inter(app.on_behalf, doc.name):
			fire_device_status(app.name, app.uri, doc)
