# -*- coding: utf-8 -*-
# Copyright (c) 2018, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import uuid
from frappe import throw, _
from frappe.model.document import Document


class IOTVirtualDevice(Document):
	def validate(self):
		if not self.sn:
			self.sn = str(uuid.uuid1()).upper()

	def before_insert(self):
		if frappe.session.user == 'Administrator':
			return
		dev_list = frappe.db.get_values('IOT Virtual Device', {"user": self.user})
		if len(dev_list) > 5:
			throw(_("Virtual device count limitation!"))

	def after_insert(self):
		doc = frappe.get_doc({
			"doctype": "IOT Device",
			"sn": self.sn,
			"dev_name": self.sn,
			"description": "Virtual Device for " + self.user,
			"owner_type": "User",
			"owner_id": self.user
		})
		doc.insert()