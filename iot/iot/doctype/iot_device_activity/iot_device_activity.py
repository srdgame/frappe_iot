# -*- coding: utf-8 -*-
# Copyright (c) 2018, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document
from frappe.utils import get_fullname, now

class IOTDeviceActivity(Document):
	def before_insert(self):
		self.full_name = get_fullname(self.user)


def on_doctype_update():
	"""Add indexes in `IOT Device Event`"""
	frappe.db.add_index("IOT Device Activity", ["device", "owner_company"])
	frappe.db.add_index("IOT Device Activity", ["owner_type", "owner_id"])


def add_device_owner_log(subject, dev_name, dev_company, owner_type=None, owner_id=None, status="Success"):
	frappe.get_doc({
		"doctype": "IOT Device Activity",
		"user": frappe.session.user,
		"status": status,
		"operation": "Owner",
		"subject": subject,
		"device": dev_name,
		"owner_type": owner_type,
		"owner_id": owner_id,
		"owner_company": dev_company,
	}).insert(ignore_permissions=True)


def add_device_status_log(subject, dev_doc, device_status, last_updated, status="Success"):
	frappe.get_doc({
		"doctype": "IOT Device Activity",
		"user": frappe.session.user,
		"status": status,
		"operation": "Status",
		"subject": subject,
		"device": dev_doc.name,
		"owner_type": dev_doc.owner_type,
		"owner_id": dev_doc.owner_id,
		"owner_company": dev_doc.company,
		"message": json.dump({
			"device_status": device_status,
			"last_updated": last_updated,
		})
	}).insert(ignore_permissions=True)


def clear_device_activity_logs():
	"""clear 100 day old authentication logs"""
	frappe.db.sql("""delete from `tabIOT Device Activity` where creation<DATE_SUB(NOW(), INTERVAL 100 DAY)""")