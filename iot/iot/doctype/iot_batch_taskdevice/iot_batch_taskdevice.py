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
		except Exception as ex:
			frappe.logger(__name__).error(_("Run batch script {0} on {1} failed. {2}").format(task.name, self.device, repr(ex)))
			self.__set_val("status", 'Error')
			self.__set_val("info", repr(ex))
		finally:
			frappe.db.commit()

	def __get_action_result(self):
		id = self.get("action_id")
		result = get_action_result(id)
		if result is None:
			return "Running"
		# print("Action result", result)
		if result.get('result') is True or result.get('result') == 'True' or result.get('result') == 'true':
			running = 0
			done = 0
			err = 0
			sub_list = result.get("message")
			msg = ""
			for sub in sub_list:
				result = get_action_result(sub.get("id"))
				if result:
					# print("Sub Action result", result)
					if result.get('result') is True or result.get('result') == 'True' or result.get('result') == 'true':
						done = done + 1
					else:
						err = err + 1
						msg = msg + "Action id: {0}\r\nTimestamp: {1}\r\nMessage: {2}\r\n".format(
							result.get("id"),
							result.get("timestamp_str"),
							result.get("message"))
				else:
					running = running + 1
			if running > 0:
				ret = "Partial"
			else:
				if err + done == len(sub_list):
					if err == 0:
						ret = "Finished"
						self.__set_val("info", "Time: {0} Message: Finished tasks {1}".format(now(), done))
					else:
						ret = "Error"
						self.__set_val("info", "Time: {0}\r\nError: {1}\r\nCompleted: {2}\r\nMessage:{3}".format(now(), err, done, msg))
			self.__set_val("status", ret)
			frappe.db.commit()
			return ret
		else:
			self.__set_val("status", "Error")
			self.__set_val("info", "Failed Time: {0} Error: {1}".format(result.get("timestamp_str"), result.get("message")))
			frappe.db.commit()
			return "Error"

	def update_status(self):
		task = frappe.get_doc("IOT Batch Task", self.parent)
		timeout = task.timeout
		start_time = self.get("action_starttime")
		if not start_time:
			self.__set_val("status", "Error")
			self.__set_val("info", "Timeout!! action_starttime is empty!")
			frappe.db.commit()
			return "Error"

		time_delta = now_datetime() - get_datetime(self.get("action_starttime"))
		if time_delta.total_seconds() >= timeout:
			self.__set_val("status", "Error")
			self.__set_val("info", "Timeout!! %d %d" % (time_delta.total_seconds(), timeout))
			frappe.db.commit()
			return "Error"

		return self.__get_action_result()
