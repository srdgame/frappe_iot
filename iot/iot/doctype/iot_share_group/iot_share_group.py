# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw, _
from frappe.model.document import Document
from cloud.cloud.doctype.cloud_company.cloud_company import list_user_companies


class IOTShareGroup(Document):

	def validate(self):
		if not frappe.session.user:
			raise frappe.PermissionError
		for user in self.users:
			if self.comany in list_user_companies(user):
				throw(_("Cannot your employee {0} into shared group").format(user))

		for device in self.devices:
			if self.company != frappe.get_value("IOT Device", device, "company"):
				throw(_("Cannot device {0} which is not belongs to your company").format(device))

	def append_devices(self, *devices):
		"""Add groups to user"""
		current_devices = [d.group for d in self.get("devices")]
		for device in devices:
			if device in current_devices:
				continue
			if self.company != frappe.get_value("IOT Device", device, "company"):
				throw(_("Cannot device {0} which is not belongs to your company").format(device))
			self.append("devices", {"device": device})

	def add_devices(self, *devices):
		"""Add groups to user and save"""
		self.append_groups(*devices)
		self.save()

	def remove_devices(self, *devices):
		existing_devices = dict((d.group, d) for d in self.get("devices"))
		for device in devices:
			if device in existing_devices:
				self.get("devices").remove(existing_devices[device])

		self.save()

	def append_users(self, *users):
		"""Add groups to user"""
		current_users = [d.group for d in self.get("users")]
		for user in users:
			if user in current_users:
				continue
			if self.comany in list_user_companies(user):
				throw(_("Cannot your employee {0} into shared group").format(user))
			self.append("users", {"user": user})

	def add_users(self, *users):
		"""Add groups to user and save"""
		self.append_groups(*users)
		self.save()

	def remove_users(self, *users):
		existing_users = dict((d.group, d) for d in self.get("users"))
		for user in users:
			if user in existing_users:
				self.get("users").remove(existing_users[user])

		self.save()