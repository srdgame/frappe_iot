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

		min_timeout = (frappe.get_conf().scheduler_interval or 240)
		if self.timeout < min_timeout:
			throw(_("Timeout must be bigger than system scheduler running time {0}!".format(min_timeout)))

	def on_update(self):
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
		frappe.logger(__name__).error(_("IOT Batch Task: mame {0} task_name {1}").format(self.name, self.task_name))
		if self.status != 'Running':
			return

		device_list = self.get("device_list")
		done = 0
		err = 0
		partial = 0
		running = 0
		for device in device_list:
			status = device.update_status()
			if status in ["Finished", "Error", "Partial"]:
				done = done + 1
			if status == "Error":
				err = err + 1
			if status == 'Partial':
				partial = partial + 1
			if status == 'Running':
				running = running + 1

		if done == len(device_list):
			if (err + partial) == 0:
				frappe.db.set_value("IOT Batch Task", self.name, "status", "Finished")
			else:
				if done == err:
					frappe.db.set_value("IOT Batch Task", self.name, "status", "Error")
				else:
					frappe.db.set_value("IOT Batch Task", self.name, "status", "Partial")


def check_all_task_status():
	for d in frappe.get_all("IOT Batch Task", "name", filters={"status": "Running", "docstatus": 1}):
							# filters = {"status": ["in", ["Running", "Partial"]], "docstatus": 1}):
		doc = frappe.get_doc("IOT Batch Task", d.name)
		doc.update_status()

	for d in frappe.get_all("IOT Batch Task", "name", filters={"status": "New", "docstatus": 1}):
		doc = frappe.get_doc("IOT Batch Task", d.name)
		doc.run_task()
