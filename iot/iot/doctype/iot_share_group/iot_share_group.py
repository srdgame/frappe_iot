# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import throw, _
from frappe.model.document import Document


class IOTShareGroup(Document):

	def validate(self):
		from cloud.cloud.doctype.cloud_company.cloud_company import list_user_companies

		if not frappe.session.user:
			raise frappe.PermissionError
		for user in self.users:
			if self.company in list_user_companies(user.user):
				throw(_("Cannot add your employee {0} into shared group").format(user.user))

		for device in self.devices:
			if self.company != frappe.get_value("IOT Device", device.device, "company"):
				throw(_("Device {0} is not belongs to company {1}").format(device.device, self.company))

	def append_devices(self, *devices):
		"""Add groups to user"""
		current_devices = [d.device for d in self.get("devices")]
		for device in devices:
			if device in current_devices:
				continue
			if self.company != frappe.get_value("IOT Device", device, "company"):
				throw(_("Device {0} is not belongs to company {1}").format(device, self.company))
			self.append("devices", {"device": device})

	def add_devices(self, *devices):
		"""Add groups to user and save"""
		self.append_devices(*devices)
		self.save()

	def remove_devices(self, *devices):
		existing_devices = dict((d.device, d) for d in self.get("devices"))
		for device in devices:
			if device in existing_devices:
				self.get("devices").remove(existing_devices[device])

		self.save()

	def append_users(self, *users):
		from cloud.cloud.doctype.cloud_company.cloud_company import list_user_companies

		"""Add groups to user"""
		current_users = [d.user for d in self.get("users")]
		for user in users:
			if user in current_users:
				continue
			if self.company in list_user_companies(user):
				throw(_("Cannot add your employee {0} into shared group").format(user))
			self.append("users", {"user": user})

	def add_users(self, *users):
		"""Add groups to user and save"""
		self.append_users(*users)
		self.save()

	def remove_users(self, *users):
		existing_users = dict((d.user, d) for d in self.get("users"))
		for user in users:
			if user in existing_users:
				self.get("users").remove(existing_users[user])

		self.save()


def get_permission_query_conditions(user):
	if 'IOT Manager' in frappe.get_roles(user):
		return ""
	from cloud.cloud.doctype.cloud_company.cloud_company import list_admin_companies

	ent_list = list_admin_companies(user)

	return """(`tabIOT Share Group`.company in ({user_ents}))""".format(
		user_ents='"' + '", "'.join(ent_list) + '"')


def has_permission(doc, ptype, user):
	if 'IOT Manager' in frappe.get_roles(user):
		return True

	if frappe.get_value('Cloud Company', {'admin': user, 'name': doc.company}):
		return True

	return False


@frappe.whitelist()
def add_user(group, user):
	frappe.get_doc("IOT Share Group", group).add_users([user])


@frappe.whitelist()
def remove_user(group, user):
	frappe.get_doc("IOT Share Group", group).remove_users([user])


@frappe.whitelist()
def add_device(group, device):
	frappe.get_doc("IOT Share Group", group).add_devices([device])


@frappe.whitelist()
def remove_device(group, device):
	frappe.get_doc("IOT Share Group", group).remove_device([device])
