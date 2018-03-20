# -*- coding: utf-8 -*-
# Copyright (c) 2018, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import time
from frappe import throw, _
from frappe.model.document import Document

class IOTBatchTaskDevice(Document):
	def run_batch_script(self):
		task = frappe.get_doc("IOT Batch Task", self.parent)
		if self.status != 'New':
			return

		timeout = time.time() + task.timeout

		frappe.logger(__name__).info("Run batch script {0} on device {1}".format(task.name, self.device))

		try:
			from iot.device_api import send_action, get_action_result
			task.set("status", "Running")
			id = send_action("sys", action="batch_script", device=self.device, data=task.batch_script)
			while True:
				time.sleep(5)
				if time.time() >= timeout:
					throw("Timeout!!!")
				result = get_action_result(id)
				print(result)
				if result.get('result') == True or result.get('result') == 'True':
					self.set("status", "Finished")
					self.set("info", "Script run completed")
		except Exception, e:
			frappe.logger(__name__).error(_("Run batch script {0} on {1} failed {1}").format(task.name, self.device, e.message))
			self.set("status", 'Error')
			self.set("info", e.message)
		finally:
			task.update_status()
