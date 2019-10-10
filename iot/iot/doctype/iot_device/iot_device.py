# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import traceback
import redis
import json
from frappe.model.document import Document
from frappe import _, throw
from frappe.utils import now, get_datetime, cstr
from frappe.utils import cint
from iot.iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings
from iot.iot.doctype.iot_device_activity.iot_device_activity import add_device_status_log, add_device_owner_log


class IOTDevice(Document):
	def validate(self):
		self.company = self.__get_company()
		if self.is_new():
			self.sn = self.sn.strip()
			self.name = self.name.strip()

		if self.owner_id is None or self.owner_id.strip() == "":
			self.owner_id = None
			self.owner_type = ""
		else:
			if self.owner_type is None or self.owner_type.strip() == "":
				throw(_("Owner Type cannot be empty when owner id is present!"))

		vdev_owenr = frappe.get_value("IOT Virtual Device", self.sn, "user")
		if vdev_owenr:
			if vdev_owenr != self.owner_id:
				throw(_("Cannot change owner for Virtual Device!"))
			if "User" != self.owner_type:
				throw(_("Cannot change owner type for Virtual Device!"))

	def on_update(self):
		client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/8", decode_responses=True)
		domain = frappe.get_value("Cloud Company", self.company, "domain")
		client.set(self.sn, domain)

	def after_insert(self):
		if self.owner_id:
			self.run_method('on_device_add', self.company, self.owner_type, self.owner_id)

	def before_save(self):
		if self.is_new():
			return

		org_owner_id = frappe.get_value("IOT Device", self.name, "owner_id")
		if org_owner_id != self.owner_id:
			if org_owner_id:
				org_owner_type = frappe.get_value("IOT Device", self.name, "owner_type")
				org_company = frappe.get_value("IOT Device", self.name, "company")
				self.run_method('on_device_del', org_company, org_owner_type, org_owner_id)
			if self.owner_id:
				self.run_method('on_device_add', self.company, self.owner_type, self.owner_id)

		last_updated = frappe.get_value("IOT Device", self.name, "last_updated")
		if last_updated != self.last_updated:
			self.run_method('on_device_status')

	def on_device_add(self, company, owner_type, owner_id):
		subject = _("Add device to {0}").format(owner_id)
		add_device_owner_log(subject, self.name, company, owner_type, owner_id, "Add")

	def on_device_del(self, org_company, org_owner_type, org_owner_id):
		subject = _("Remove device from {0}").format(org_owner_id)
		add_device_owner_log(subject, self.name, org_company, org_owner_type, org_owner_id, "Delete")

		# Delet from shared group
		for d in frappe.db.get_values("IOT ShareGroupDevice", {"device": self.name}, "name"):
			frappe.delete_doc("IOT ShareGroupDevice", d[0])

	def on_device_status(self):
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

	def update_owner(self, owner_type, owner_id, ignore_permissions=False):
		""" update device owner """
		if self.owner_type == owner_type and self.owner_id == owner_id:
			return
		self.set("owner_type", owner_type)
		self.set("owner_id", owner_id)
		self.save(ignore_permissions = ignore_permissions)

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

	def has_supper_permissions(self):
		if frappe.session.user == 'Administrator':
			return True
		if 'IOT Manager' in frappe.get_roles(frappe.session.user):
			return True
		return False

	def clean_activities(self):
		if not self.has_supper_permissions():
			throw(_("You have no permission to clean device activities!"))

		for d in frappe.db.get_values("IOT Device Activity", {"device": self.name}, "name"):
			frappe.delete_doc("IOT Device Activity", d[0])

	def clean_events(self):
		if not self.has_supper_permissions():
			throw(_("You have no permission to clean device events!"))

		for d in frappe.db.get_values("IOT Device Event", {"device": self.name}, "name"):
			doc = frappe.get_doc("IOT Device Event", d[0])
			doc.wechat_msg_clean()
			frappe.delete_doc("IOT Device Event", d[0])

	def strip_sn_fix(self):
		sn = self.sn.strip()
		if sn != self.sn:
			frappe.db.set_value("IOT Device", self.name, "sn", sn)

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
		except Exception as ex:
			frappe.logger(__name__).error(ex)
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

		share_role = None
		for d in frappe.db.get_values("IOT ShareGroupDevice", {"device": self.name, "parenttype": 'IOT Share Group'}, "parent"):
			if frappe.get_value("IOT ShareGroupUser", {"parent": d[0], "user": username}, "parent") == d[0]:
				if share_role != 'Admin':
					share_role = frappe.get_value("IOT Share Group", d[0], 'role')

		return share_role


def on_doctype_update():
	"""Add indexes in `IOT Device`"""
	frappe.db.add_index("IOT Device", ["company", "owner_type", "owner_id"])
	frappe.db.add_index("IOT Device", ["longitude", "latitude"])


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


def has_permission_inter(user, doc_name, company=None, owner_type=None, owner_id=None):
	company = company or frappe.get_value('IOT Device', doc_name, 'company')
	if frappe.get_value('Cloud Company', company, 'admin') == user:
		return True

	owner_type = owner_type or frappe.get_value('IOT Device', doc_name, 'owner_type')
	owner_id = owner_id or frappe.get_value('IOT Device', doc_name, 'owner_id')

	if owner_type == '' or owner_id is None:
		return False

	if owner_type == 'User' and owner_id == user:
		return True

	if owner_type == "Cloud Company Group":
		from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_users
		for d in list_users(owner_id):
			if d.name == user:
				return True

	for d in frappe.db.get_values("IOT ShareGroupDevice", {"device": doc_name, "parenttype": 'IOT Share Group'}, "parent"):
		if frappe.get_value("IOT ShareGroupUser", {"parent": d[0], "user": user}, "parent") == d[0]:
			return True

	return False


def has_permission(doc, ptype, user):
	if 'IOT Manager' in frappe.get_roles(user):
		return True

	return has_permission_inter(user, doc.name)


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


def list_tags(sn):
	return []


def add_tags(sn, *tags):
	return tags


def remove_tags(sn, *tags):
	return []


def clear_tags(sn):
	return []
