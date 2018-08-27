# -*- coding: utf-8 -*-
# Copyright (c) 2018, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, throw
from frappe.model.document import Document
from frappe.utils.data import format_datetime
from cloud.cloud.doctype.cloud_company.cloud_company import get_wechat_app
from iot.iot.doctype.iot_device.iot_device import IOTDevice


class IOTDeviceEvent(Document):
	def after_insert(self):
		if self.wechat_notify == 1 and get_wechat_app(self.owner_company):
			self.submit()

	def on_submit(self):
		if self.wechat_notify == 1:
			frappe.enqueue_doc('IOT Device Event', self.name, 'wechat_msg_send')

	def on_trash(self):
		self.wechat_msg_clean()

	def wechat_msg_clean(self):
		from wechat.api import clean_doc
		clean_doc('IOT Device Event', self.name)

	def wechat_msg_send(self):
		user_list = IOTDevice.find_owners(self.owner_type, self.owner_id)

		if len(user_list) > 0:
			app = get_wechat_app(self.owner_company)
			if app:
				from wechat.api import send_doc
				send_doc(app, 'IOT Device Event', self.name, user_list)

	def wechat_tmsg_data(self):
		remark = _("Level: {0}\nInfo: {1}\nData:{2}").format(self.event_level, self.event_info, self.event_data)
		return {
			"first": {
				"value": _("Has new device alarm"),
				"color": "#800000"
			},
			"keyword1": {
				"value": self.event_type,
				"color": "#000080"
			},
			"keyword2": {
				"value": frappe.get_value("IOT Device", self.device, "dev_name"),
				"color": "#000080"
			},
			"keyword3": {
				"value": format_datetime(self.modified),
				"color": "#008000",
			},
			"remark": {
				"value": remark
			}
		}

	def wechat_tmsg_url(self):
		return self.get_url()


	def dispose(self, disposed=1):
		self.disposed = disposed
		self.disposed_by = frappe.session.user
		self.save()


def on_doctype_update():
	"""Add indexes in `IOT Device Event`"""
	frappe.db.add_index("IOT Device Event", ["device", "owner_company"])
	frappe.db.add_index("IOT Device Event", ["owner_type", "owner_id"])


def has_permission(doc, ptype, user):
	if 'IOT Manager' in frappe.get_roles(user):
		return True

	company = frappe.get_value('IOT Device Event', doc.name, 'owner_company')
	if frappe.get_value('Cloud Company', {'admin': user, 'name': company}):
		return True

	owner_type = frappe.get_value('IOT Device Event', doc.name, 'owner_type')
	owner_id = frappe.get_value('IOT Device Event', doc.name, 'owner_id')

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


def clear_device_events():
	"""clear 100 day old iot device events"""
	frappe.db.sql("""delete from `tabIOT Device Event` where creation<DATE_SUB(NOW(), INTERVAL 100 DAY)""")


event_fields = ["name", "device", "event_source", "event_level", "event_type", "event_info", "event_data", "event_time", "wechat_notify", "creation"]


def query_device_event_by_user(user, start=None, limit=None, filters=None):
	from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups
	groups = [g.name for g in list_user_groups(user)]
	groups.append(user)

	filters = filters or {}
	filters.update({
		"owner_id": ["in", groups]
	})
	return frappe.get_all('IOT Device Event', fields=event_fields, filters=filters, order_by="creation desc", start=start, limit=limit)


def count_device_event_by_user(user, filters=None):
	from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups
	groups = [g.name for g in list_user_groups(user)]
	groups.append(user)

	filters = filters or {}
	filters.update({
		"owner_id": ["in", groups]
	})
	return frappe.db.count('IOT Device Event', filters=filters)


def query_device_event(sn=None, start=None, limit=None, filters=None):
	#frappe.logger(__name__).debug(_("query_device_event {0}").format(company))
	if not sn:
		return query_device_event_by_user(frappe.session.user, start, limit, filters)

	filters = filters or {}
	filters.update({
		"device": sn
	})
	return frappe.get_all('IOT Device Event', fields=event_fields, filters=filters, order_by="creation desc", start=start, limit=limit)


def count_device_event(sn=None, filters=None):
	if not sn:
		return count_device_event_by_user(frappe.session.user)

	filters = filters or {}
	filters.update({
		"device": sn
	})
	return frappe.db.count('IOT Device Event', filters=filters)


def query_device_event_by_company(company, start=None, limit=None, filters=None):
	filters = filters or {}
	filters.update({
		"owner_company": company
	})
	return frappe.get_all('IOT Device Event', fields=event_fields, filters=filters, order_by="creation desc", start=start, limit=limit)


def count_device_event_by_company(company, filters=None):
	filters = filters or {}
	filters.update({
		"owner_company": company
	})
	return frappe.db.count('IOT Device Event', filters=filters)