# -*- coding: utf-8 -*-
# Copyright (c) 2018, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import time
from frappe import throw, _
from frappe.model.document import Document


class IOTBatchTask(Document):
	def on_update(self):
		if not self.owner_id:
			self.owner_id = frappe.session.user
		if self.status == 'New':
			for device in self.get("device_list"):
				device.status = 'New'
				device.info = ''

	def on_submit(self):
		frappe.enqueue_doc('IOT Batch Task', self.name, 'run_task')

	def run_task(self):
		if self.status in ["Error", "Finished", "Partial", "Running"]:
			return

		device_list = self.get("device_list")

		for device in device_list:
			frappe.enqueue_doc('IOT Batch TaskDevice', device.name, 'run_batch_script')

		frappe.db.set_value("IOT Batch Task", self.name, "status", "Running")

	def update_status(self):
		print("========================= check_all_task_status ==============================")
		print("Task Name", self.name, self.task_name)
		if self.status != 'Running':
			return
		device_list = self.get("device_list")
		done = 0
		for device in device_list:
			status = device.update_status()
			if status in ["Finished", "Error"]:
				done = done + 1

		if done < len(device_list) and done > 0:
			frappe.db.set_value("IOT Batch Task", self.name, "status", "Partial")
		if done == len(device_list):
			frappe.db.set_value("IOT Batch Task", self.name, "status", "Finished")


def check_all_task_status():
	for d in frappe.get_all("IOT Batch Task", "name", filters={"status": ["in", ["New", "Partial"]], "docstatus": 1}):
		doc = frappe.get_doc("IOT Batch task", d.name)
		doc.update_status()