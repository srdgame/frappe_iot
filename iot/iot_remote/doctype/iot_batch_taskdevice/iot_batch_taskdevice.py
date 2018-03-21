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
	def __set_val(self, dt, dv):
		frappe.db.set_value("IOT Batch TaskDevice", self.name, dt, dv)

	def run_batch_script(self):
		task = frappe.get_doc("IOT Batch Task", self.parent)
		if self.status != 'New':
			return

		frappe.logger(__name__).info("Run batch script {0} on device {1}".format(task.name, self.device))

		try:
			id = send_action("sys", action="batch_script", device=self.device, data=task.batch_script)
			if not id:
				throw("Send action failed")
			self.__set_val("status", "Running")
			self.__set_val("action_id", id)
			self.__set_val("action_starttime", now())
		except Exception, e:
			frappe.logger(__name__).error(_("Run batch script {0} on {1} failed. {2}").format(task.name, self.device, e.message))
			self.__set_val("status", 'Error')
			self.__set_val("info", e.message)
		finally:
			frappe.db.commit()

	def update_status(self):
		task = frappe.get_doc("IOT Batch Task", self.parent)
		timeout = task.timeout
		time_delta = now_datetime() - get_datetime(self.get("action_starttime"))
		if time_delta.total_seconds() >= timeout:
			self.__set_val("status", "Error")
			self.__set_val("info", "Timeout!!")
			frappe.db.commit()
			return "Error"

		id = self.get("action_id")
		result = get_action_result(id)
		if result:
			if result.get('result') == True or result.get('result') == 'True':
				self.__set_val("status", "Finished")
				self.__set_val("info", "Script run completed")
				frappe.db.commit()
				return "Finished"

		return self.get("status")