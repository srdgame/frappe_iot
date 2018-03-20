# -*- coding: utf-8 -*-
# Copyright (c) 2018, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import time
from frappe import throw, _
from frappe.model.document import Document


class IOTBatchTask(Document):
	def validate(self):
		if not self.owner_id:
			self.owner_id = frappe.session.user

	def on_submit(self):
		frappe.enqueue_doc('IOT Batch Task', self.name, 'run_task')

	def run_task(self):
		if self.status in ["Error", "Finished", "Partial"]:
			return

		if self.status == 'Running':
			return self.update_status()

		device_list = self.get("device_list")

		for device in device_list:
			frappe.enqueue_doc('IOT Batch TaskDevice', device.name, 'run_batch_script')

		frappe.db.set_value("IOT Batch Task", self.name, "status", "Running")

	def update_status(self):
		device_list = self.get("device_list")
		partial = False
		for device in device_list:
			device.update_status()
			status = device.get("status")
			if status in ["New", "Running"]:
				return
			if status in ["Error", "Partial"]:
				partial = True
		if not partial:
			frappe.db.set_value("IOT Batch Task", self.name, "status", "Finished")
		else:
			frappe.db.set_value("IOT Batch Task", self.name, "status", "Partial")

