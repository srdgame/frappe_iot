# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw, _
from frappe.model.document import Document


class IOTConfigBundle(Document):
	def validate(self):
		for dev in self.devices:
			dev.device_name = frappe.get_value("IOT Device", dev.device, "dev_name")
			if frappe.get_value("IOT Device Config", dev.device):
				sid = frappe.get_value("IOT Device Config", dev.device, "source_id")
				if sid != self.name:
					throw(_("Device SN {0} is licensed by {1}").format(dev.device, sid))

		self.config_name = frappe.get_value("IOT Config", self.config, "config_name")

	def after_insert(self):
		for dev in self.devices:
			doc = frappe.get_doc({
				"doctype": "IOT Device Config",
				"device": dev.device,
				"config": self.config,
				"version": self.config_version,
				"source_type": self.doctype,
				"source_id": self.name
			}).insert()

	def on_update(self):
		dev_list = [d.device for d in self.devices]
		for d in frappe.db.get_values("IOT Device Config", {"source_id": self.name}, "device"):
			if d[0] not in dev_list:
				frappe.delete_doc("IOT Device Config", d[0])
			else:
				frappe.set_value("IOT Device Config", d[0], "version", self.config_version)
				frappe.set_value("IOT Device Config", d[0], "config", self.config)

		for dev in self.devices:
			if not frappe.get_value("IOT Device Config", dev.device):
				doc = frappe.get_doc({
					"doctype": "IOT Device Config",
					"device": dev.device,
					"config": self.config,
					"version": self.config_version,
					"source_type": self.doctype,
					"source_id": self.name
				}).insert()

	def on_trash(self):
		for dev in self.devices:
			frappe.delete_doc("IOT Device Config", dev.device)