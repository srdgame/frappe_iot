# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import traceback
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, cstr
from frappe.utils import cint
from cloud.cloud.doctype.cloud_settings.cloud_settings import CloudSettings

class IOTDevice(Document):
	def validate(self):
		self.company = self.__get_company()

	def update_status(self, status):
		""" update device status """
		if self.device_status == status:
			return
		self.set("device_status", status)
		self.set("last_updated", now())
		self.save()

	def update_bunch(self, bunch):
		""" update device bunch code """
		if self.bunch == bunch:
			return
		self.set("bunch", bunch)
		self.set("last_updated", now())
		self.save()

	def update_hdb(self, hdb):
		""" update device hdb"""
		if self.hdb == hdb:
			return
		self.set("hdb", hdb)
		self.set("last_updated", now())
		self.save()

	def update_dev_name(self, dev_name):
		if self.dev_name == dev_name:
			return
		self.set("dev_name", dev_name)
		self.set("last_updated", now())
		self.save()

	@staticmethod
	def check_sn_exists(sn):
		return frappe.db.get_value("IOT Device", {"sn": sn}, "sn")

	@staticmethod
	def list_device_sn_by_bunch(bunch):
		return [d[0] for d in frappe.db.get_values("IOT Device", {"bunch": bunch}, "sn")]

	@staticmethod
	def get_device_doc(sn):
		dev = None
		try:
			dev = frappe.get_doc("IOT Device", sn)
		except Exception, e:
			frappe.logger(__name__).error(e)
			traceback.print_exc()
		finally:
			frappe.logger(__name__).error(_("Device {0} does not exits!").format(sn))
		return dev

	@staticmethod
	def find_owners_by_bunch(bunch):
		if not bunch:
			return []
		code = frappe.get_doc("IOT Device Bunch", bunch)

		id = code.get("owner_id")
		if code.get("owner_type") == "User":
			return [id]

		if code.get("owner_type") == "IOT Employee Group":
			return frappe.db.get_values("IOT UserGroup", {"group": id}, "parent")

		raise Exception("You should got here!")

	def __get_company(self):
		if not self.bunch:
			return None
		bunch = frappe.get_doc("IOT Device Bunch", self.bunch)
		if not bunch:
			return None
		if bunch.owner_type == "User":
			return CloudSettings.get_default_company()
		else:
			return frappe.get_value(bunch.owner_type, bunch.owner_id, "parent")

	def has_website_permission(self, ptype, verbose=False):
		user = frappe.session.user
		bunch = frappe.get_doc("IOT Device Bunch", self.bunch)
		if bunch.owner_type == "User" and bunch.owner_id == user:
			return True

		if self.company is not None:
			if not cint(frappe.get_value('IOT Enterprise', self.company, 'enabled')):
				return False

		groups = [d[0] for d in frappe.db.get_values('IOT UserGroup', {"parent": user}, "group")]
		ent = frappe.get_value("IOT Enterprise", {"admin": user})
		if ent:
			groups = [d[0] for d in frappe.db.get_values('IOT Employee Group', {'parent': ent}, "name")]

		if bunch.owner_type == "IOT Employee Group" and bunch.owner_id in groups:
			return True

		return False


def get_device_list(doctype, txt, filters, limit_start, limit_page_length=20, order_by="modified desc"):
	ent = frappe.get_value('IOT User', frappe.session.user, 'company')
	if not ent or not cint(frappe.get_value('IOT Enterprise', ent, 'enabled')):
		return frappe.db.sql('''select distinct device.*
		from `tabIOT Device` device, `tabIOT Device Bunch` bunch_code 
		where
			(bunch_code.owner_type = "User"
			and bunch_code.owner_id = %(user)s
			and bunch_code.code = device.bunch)
			order by device.{0}
			limit {1}, {2}
		'''.format(order_by, limit_start, limit_page_length),
			{'user':frappe.session.user},
			as_dict=True,
			update={'doctype':'IOT Device'})

	ent = frappe.get_value("IOT Enterprise", {"admin": frappe.session.user})
	if ent:
		return frappe.db.sql('''select distinct device.*
		from `tabIOT Device` device, `tabIOT Employee Group` em_group, `tabIOT Device Bunch` bunch_code 
		where
			(bunch_code.owner_type = "User"
			and bunch_code.owner_id = %(user)s
			and bunch_code.code = device.bunch)
			or (bunch_code.owner_type = "IOT Employee Group"
			and em_group.name = bunch_code.owner_id
			and em_group.parent = %(ent)s
			and bunch_code.code = device.bunch)
			order by device.{0}
			limit {1}, {2}
		'''.format(order_by, limit_start, limit_page_length),
			{'user' : frappe.session.user, 'ent': ent},
			as_dict=True,
			update={'doctype' : 'IOT Device'})

	return frappe.db.sql('''select distinct device.*
		from `tabIOT Device` device, `tabIOT UserGroup` user_group, `tabIOT Device Bunch` bunch_code 
		where
			(bunch_code.owner_type = "User"
			and bunch_code.owner_id = %(user)s
			and bunch_code.code = device.bunch)
			or (bunch_code.owner_type = "IOT Employee Group"
			and user_group.group = bunch_code.owner_id
			and user_group.parent = %(user)s
			and bunch_code.code = device.bunch)
			order by device.{0}
			limit {1}, {2}
		'''.format(order_by, limit_start, limit_page_length),
			{'user':frappe.session.user},
			as_dict=True,
			update={'doctype':'IOT Device'})


def get_list_context(context=None):
	return {
		"show_sidebar": True,
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
