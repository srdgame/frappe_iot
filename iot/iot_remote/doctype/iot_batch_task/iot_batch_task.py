# -*- coding: utf-8 -*-
# Copyright (c) 2018, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw, _
from frappe.model.document import Document


class IOTBatchTask(Document):
	def validate(self):
		self.owner_id = frappe.session.user

	def on_submit(self):
		frappe.enqueue_doc('IOT Batch Task', self.name, 'run_task')

	def run_task(self):
		if self.docstatus != 1:
			return
		if self.status in ["Error", "Finished"]:
			return

		device_list = self.get("device_list")

		for device in device_list:
			frappe.enqueue_doc('IOT Batch TaskDevice', device.name, 'run_batch_script')

		self.set("status", "Running")
		self.save()

	def update_status(self):
		device_list = self.get("device_list")
		count = 0
		for device in device_list:
			status = device.get("status")
			if status in ["New", "Running"]:
				return

		self.set("status", "Finished")