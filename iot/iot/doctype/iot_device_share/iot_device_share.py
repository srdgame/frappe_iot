# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw
from frappe.model.document import Document
from frappe.utils.data import get_datetime_str
from iot.iot.doctype.iot_device_activity.iot_device_activity import add_device_owner_log
from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups


class IOTDeviceShare(Document):
	def validate(self):
		org_share = frappe.get_value("IOT Device Share", {"device": self.device, "share_to": self.share_to}, "name")
		if org_share and org_share != self.name:
			throw("device_already_shared_to_this_user")

		if 'IOT Manager' in frappe.get_roles():
			return

		owner_type = frappe.get_value("IOT Device", self.device, "owner_type")
		if owner_type == 'User':
			if frappe.get_value("IOT Device", self.device, "owner_id") != frappe.session.user:
				throw("you_are_not_owner_of_this_device")
		else:
			group = frappe.get_value("IOT Device", self.device, "owner_id")
			got_group = False
			for g in list_user_groups(frappe.session.user):
				if g.name == group:
					got_group = True
					break
			if not got_group:
				throw("you_are_not_owner_of_this_device")

	def before_save(self):
		if self.is_new():
			return
		org_end_time = frappe.get_value("IOT Device Share", self.name, "end_time")
		if org_end_time != self.end_time:
			subject = "Share device {0} to {1} updated".format(self.device, self.share_to)
			doc = frappe.get_doc("IOT Device", self.device)
			add_device_owner_log(subject, self.device, doc.company, doc.owner_type, doc.owner_id, message={
				"action": "UpdateShare",
				"device": self.device,
				"share_to": self.share_to,
				"end_time": get_datetime_str(self.end_time)
			})

	def after_insert(self):
		subject = "Share device {0} to {1}".format(self.device, self.share_to)
		doc = frappe.get_doc("IOT Device", self.device)
		add_device_owner_log(subject, self.device, doc.company, doc.owner_type, doc.owner_id, message={
			"action": "DeleteShare",
			"device": self.device,
			"share_to": self.share_to,
			"end_time": get_datetime_str(self.end_time)
		})

	def on_trash(self):
		subject = "Device share {0} to {1} deleted".format(self.device, self.share_to)
		doc = frappe.get_doc("IOT Device", self.device)
		add_device_owner_log(subject, self.device, doc.company, doc.owner_type, doc.owner_id, message={
			"action": "AddShare",
			"device": self.device,
			"share_to": self.share_to,
			"end_time": get_datetime_str(self.end_time)
		})


def clear_device_shares():
	"""clear 100 day old iot device share"""
	frappe.db.sql("""delete from `tabIOT Device Share` where creation<DATE_SUB(NOW(), INTERVAL 100 DAY)""")