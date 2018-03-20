# -*- coding: utf-8 -*-
# Copyright (c) 2018, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import time
from frappe import throw, _
from frappe.model.document import Document
from frappe.utils import now, now_datetime, get_datetime
from iot.device_api import send_action, get_action_result


class IOTBatchTaskDevice(Document):
	def run_batch_script(self):
		task = frappe.get_doc("IOT Batch Task", self.parent)
		if self.status != 'New':
			return

		frappe.logger(__name__).info("Run batch script {0} on device {1}".format(task.name, self.device))

		try:
			id = send_action("sys", action="batch_script", device=self.device, data=task.batch_script)
			if not id:
				throw("Send action failed")
			task.set("status", "Running")
			self.set("action_id", id)
			self.set("action_startime", now())
		except Exception, e:
			frappe.logger(__name__).error(_("Run batch script {0} on {1} failed {1}").format(task.name, self.device, e.message))
			self.set("status", 'Error')
			self.set("info", e.message)
		finally:
			task.update_status(task)

	def update_status(self, task=None):
		task = task or frappe.get_doc("IOT Batch Task", self.parent)
		timeout = task.timeout
		time_delta = now_datetime() - get_datetime(self.get("action_startime"))
		if time_delta.total_seconds() >= timeout:
			self.set("status", "Error")
			self.set("info", "Timeout!!")
		else:
			result = get_action_result(id)
			print(result)
			if result.get('result') == True or result.get('result') == 'True':
				self.set("status", "Finished")
				self.set("info", "Script run completed")

		self.save()