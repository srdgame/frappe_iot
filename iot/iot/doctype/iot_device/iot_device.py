# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import traceback
import redis
import json
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, cstr
from frappe.utils import cint
from iot.iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings
from iot.iot.doctype.iot_device_activity.iot_device_activity import add_device_status_log, add_device_owner_log


class IOTDevice(Document):
	def validate(self):
		self.company = self.__get_company()

	def on_update(self):
		client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/8")
		domain = frappe.get_value("Cloud Company", self.company, "domain")
		client.set(self.sn, domain)

	def after_insert(self):
		if self.owner_id:
			subject = _("Add device to {0}").format(self.owner_id)
			add_device_owner_log(subject, self.name, self.company, self.owner_type, self.owner_id)

	def before_save(self):
		if self.is_new():
			return

		org_owner_id = frappe.get_value("IOT Device", self.name, "owner_id")
		if org_owner_id != self.owner_id:
			if org_owner_id:
				org_owner_type = frappe.get_value("IOT Device", self.name, "owner_type")
				subject = _("Remove device from {0}").format(org_owner_id)
				add_device_owner_log(subject, self.name, self.company, org_owner_type, org_owner_id)
			if self.owner_id:
				subject = _("Add device to {0}").format(self.owner_id)
				add_device_owner_log(subject, self.name, self.company,  self.owner_type, self.owner_id)
		last_updated = frappe.get_value("IOT Device", self.name, "last_updated")
		if last_updated != self.last_updated:
			if self.device_status == 'ONLINE':
				subject = _("Device {0} connected").format(self.name)
			else:
				subject = _("Device {0} disconnected").format(self.name)
			add_device_status_log(subject, self, self.device_status, self.last_updated)


	def update_status(self, status):
		""" update device status """
		self.set("device_status", status)
		self.set("last_updated", now())
		self.save(ignore_version=True)

	def update_owner(self, owner_type, owner_id):
		""" update device owner """
		if self.owner_type == owner_type and self.owner_id == owner_id:
			return
		self.set("owner_type", owner_type)
		self.set("owner_id", owner_id)
		self.save()

	def update_hdb(self, hdb):
		""" update device hdb"""
		if self.hdb == hdb:
			return
		self.set("hdb", hdb)
		self.save()

	def update_dev_name(self, dev_name):
		if self.dev_name == dev_name:
			return
		self.set("dev_name", dev_name)
		self.save()

	def update_dev_description(self, desc):
		if self.description == desc:
			return
		self.set("description", desc)
		self.save()

	def update_dev_pos(self, longitude, latitude):
		self.set("longitude", longitude)
		self.set("latitude", latitude)
		self.save()

	def set_use_beta(self):
		if self.use_beta != 0 and self.use_beta_start_time:
			return
		self.set('use_beta', 1)
		self.set("use_beta_start_time", now())
		self.save()

	@staticmethod
	def check_sn_exists(sn):
		return frappe.db.get_value("IOT Device", {"sn": sn}, "sn")

	@staticmethod
	def list_device_sn_by_owner(owner_id):
		return [d[0] for d in frappe.db.get_values("IOT Device", {"owner_id": owner_id}, "sn")]

	@staticmethod
	def get_device_doc(sn):
		dev = None
		try:
			dev = frappe.get_doc("IOT Device", sn)
		except Exception, e:
			frappe.logger(__name__).error(e)
			#traceback.print_exc()
		return dev

	@staticmethod
	def find_owners(owner_type, owner_id):
		from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_users

		if not owner_id:
			return []

		if owner_type == "User":
			return [owner_id]

		if owner_type == "Cloud Company Group":
			return [user.name for user in list_users(owner_id)]

		raise Exception("You should got here!")

	def __get_company(self):
		from cloud.cloud.doctype.cloud_settings.cloud_settings import CloudSettings

		if not self.owner_id:
			return CloudSettings.get_default_company()

		if self.owner_type == "User":
			return CloudSettings.get_default_company()
		else:
			return frappe.get_value(self.owner_type, self.owner_id, "company")

	def list_owners(self):
		return self.find_owners(self.owner_type, self.owner_id)

	def get_role_permission(self, username):
		from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_users

		if not self.owner_id:
			return None
		if self.owner_type == 'User':
			if self.owner_id == username:
				return 'Admin'
		else:
			for user in list_users(self.owner_id):
				if user.name == username:
					return user.role
		return None


def get_permission_query_conditions(user):
	"""
	Show devices for Company Administrator
	:param user: 
	:return: 
	"""
	if 'IOT Manager' in frappe.get_roles(user):
		return ""
	from cloud.cloud.doctype.cloud_company.cloud_company import list_admin_companies

	ent_list = list_admin_companies(user)

	return """(`tabIOT Device`.company in ({user_ents}))""".format(
		user_ents='"' + '", "'.join(ent_list) + '"')


def has_permission(doc, ptype, user):
	if 'IOT Manager' in frappe.get_roles(user):
		return True

	company = frappe.get_value('IOT Device', doc.name, 'company')
	if frappe.get_value('Cloud Company', {'admin': user, 'name': company}):
		return True

	owner_type = frappe.get_value('IOT Device', doc.name, 'owner_type')
	owner_id = frappe.get_value('IOT Device', doc.name, 'owner_id')

	if owner_type == 'User' and owner_id == user:
		return True

	if owner_type == "Cloud Company Group":
		from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_users
		for d in list_users(owner_id):
			if d.name == user:
				return True

	if owner_type == '' and owner_id == None:
		return True

	return False


def get_device_list(doctype, txt, filters, limit_start, limit_page_length=20, order_by="modified desc"):
	from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups

	groups = [d.name for d in list_user_groups(frappe.session.user)]
	if len(groups) == 0:
		return frappe.db.sql('''select *
			from `tabIOT Device` 
			where
				`tabIOT Device`.owner_type = "User"
				and `tabIOT Device`.owner_id = %(user)s
				order by device.{0}
				limit {1}, {2}
			'''.format(order_by, limit_start, limit_page_length),
				{'user' : frappe.session.user},
				as_dict=True,
				update={'doctype':'IOT Device'})

	return frappe.db.sql('''select *
		from `tabIOT Device`
		where
			(`tabIOT Device`.owner_type = "User"
			and `tabIOT Device`.owner_id = %(user)s)
			or (`tabIOT Device`.owner_type = "Cloud Company Group"
			and `tabIOT Device`.owner_id in {3})
			order by device.{0}
			limit {1}, {2}
		'''.format(order_by, limit_start, limit_page_length, "('"+"','".join(groups)+"')"),
			{'user' : frappe.session.user},
			as_dict=True,
			update={'doctype' : 'IOT Device'})


def get_list_context(context=None):
	return {
		"show_sidebar": False,
		"show_search": True,
		"no_breadcrumbs": True,
		"title": _("Your Devices"),
		#"introduction": _('IOT Devices of your group/account'),
		"get_list": get_device_list,
		"row_template": "templates/generators/iot_device_row.html",
	}


@frappe.whitelist()
def list_device_map():
	return get_device_list('IOT Device', '', '*', limit_start=0, limit_page_length=10000)


@frappe.whitelist()
def list_device_map2():
	devices = frappe.get_all('IOT Device', fields=["sn", "dev_name", "longitude", "latitude", "device_status", "last_updated"])
	for dev in devices:
		if not dev.longitude:
			dev.longitude = '116.3252'
		if not dev.latitude:
			dev.latitude = '40.045103'
	return devices
