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
		frappe.enqueue_doc('IOT Batch Task', self.name, 'run_task', timeout=self.timeout + 60)

	def run_task(self):
		if self.status in ["Error", "Finished"]:
			return

		device_list = self.get("device_list")
		timeout = self.timeout + 60

		for device in device_list:
			frappe.enqueue_doc('IOT Batch TaskDevice', device.name, 'run_batch_script', timeout=timeout)

		frappe.db.set_value("IOT Batch Task", self.name, "status", "Running")

		time.sleep(self.timeout)
		self.update_status()

	def update_status(self):
		device_list = self.get("device_list")
		for device in device_list:
			status = device.get("status")
			if status in ["New", "Running"]:
				return

		frappe.db.set_value("IOT Batch Task", self.name, "status", "Finished")
