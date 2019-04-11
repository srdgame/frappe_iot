# -*- coding: utf-8 -*-
# Copyright (c) 2018, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import requests
from frappe import _,throw, _dict
from frappe.model.document import Document
from frappe.utils import get_fullname, now, get_datetime_str

class IOTDeviceActivity(Document):
	def before_insert(self):
		self.full_name = get_fullname(self.user)


	def dispose(self, disposed=1):
		self.disposed = disposed
		self.disposed_by = frappe.session.user
		self.save(ignore_permissions=True)


	# def after_insert(self):
	# 	self.insert_to_influxdb()
	#
	# def insert_to_influxdb(self):
	# 	from iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings
	# 	inf_server = IOTHDBSettings.get_influxdb_server()
	# 	if not inf_server:
	# 		frappe.logger(__name__).error("InfluxDB Configuration missing in IOTHDBSettings")
	# 		return
	#
	# 	dp = 'iot_device_activity,iot=' + self.device + ',device=' + self.device + ' activity=' + vsn + '\''
	#
	# 	domain = frappe.get_value("Cloud Company", self.onwer_company, "domain")
	# 	r = requests.session().get(inf_server + "/write", params={"db": domain}, timeout=10, data=dp)
	# 	if r.status_code == 200:
	# 		return r.json()["results"] or r.json()
	#
	# 	return r.text


def on_doctype_update():
	"""Add indexes in `IOT Device Event`"""
	frappe.db.add_index("IOT Device Activity", ["device", "owner_company"])
	frappe.db.add_index("IOT Device Activity", ["owner_type", "owner_id"])


def has_permission(doc, ptype, user):
	if 'IOT Manager' in frappe.get_roles(user):
		return True

	company = frappe.get_value('IOT Device Activity', doc.name, 'owner_company')
	if frappe.get_value('Cloud Company', {'admin': user, 'name': company}):
		return True

	owner_type = frappe.get_value('IOT Device Activity', doc.name, 'owner_type')
	owner_id = frappe.get_value('IOT Device Activity', doc.name, 'owner_id')

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


def add_device_owner_log(subject, dev_name, dev_company, owner_type=None, owner_id=None, action="Add", status="Success"):
	frappe.get_doc({
		"doctype": "IOT Device Activity",
		"user": frappe.session.user,
		"status": status,
		"operation": "Owner",
		"subject": subject,
		"device": dev_name,
		"owner_type": owner_type,
		"owner_id": owner_id,
		"owner_company": dev_company,
		"message": json.dumps({
			"action": action
		})
	}).insert(ignore_permissions=True)


def add_device_status_log(subject, dev_doc, device_status, last_updated, status="Success"):
	frappe.get_doc({
		"doctype": "IOT Device Activity",
		"user": frappe.session.user,
		"status": status,
		"operation": "Status",
		"subject": subject,
		"device": dev_doc.name,
		"owner_type": dev_doc.owner_type,
		"owner_id": dev_doc.owner_id,
		"owner_company": dev_doc.company,
		"message": json.dumps({
			"device_status": device_status,
			"last_updated": last_updated,
		})
	}).insert(ignore_permissions=True)


def add_device_action_log(dev_doc, channel, action, id, data, status="Success", message=None):
	frappe.get_doc({
		"doctype": "IOT Device Activity",
		"user": frappe.session.user,
		"status": status,
		"operation": "Action",
		"subject": _("Device action {0} - {1}").format(channel, action),
		"device": dev_doc.name,
		"owner_type": dev_doc.owner_type,
		"owner_id": dev_doc.owner_id,
		"owner_company": dev_doc.company,
		"message": json.dumps({
			"channel": channel,
			"action": action or channel,
			"id": id,
			"data": data or "",
			"message": message or ""
		})
	}).insert(ignore_permissions=True)


def clear_device_activities():
	"""clear 100 day old iot device activities"""
	frappe.db.sql("""delete from `tabIOT Device Activity` where creation<DATE_SUB(NOW(), INTERVAL 100 DAY)""")


activity_fields = ["name", "subject", "operation", "status", "message", "disposed", "disposed_by", "device", "user", "full_name", "creation"]


def get_log_detail(name):
	doc = frappe.get_doc("IOT Device Activity", name)
	data = _dict({})
	for key in activity_fields:
		data[key] = doc.get(key)
	return data


def query_logs_by_user(user, start=None, limit=None, filters=None):
	from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups
	groups = [g.name for g in list_user_groups(user)]
	groups.append(user)

	filters = filters or {}
	filters.update({
		"owner_id": ["in", groups]
	})
	return frappe.get_all('IOT Device Activity', fields=activity_fields, filters=filters, order_by="creation desc", start=start, limit=limit)


def count_logs_by_user(user, filters=None):
	from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups
	groups = [g.name for g in list_user_groups(user)]
	groups.append(user)

	filters = filters or {}
	filters.update({
		"owner_id": ["in", groups]
	})
	return frappe.db.count('IOT Device Activity', filters=filters)


def query_logs_by_company(company, start=None, limit=None, filters=None):
	#frappe.logger(__name__).debug(_("query_device_logs_by_company {0}").format(company))
	filters = filters or {}
	filters.update({
		"owner_company": company
	})
	return frappe.get_all('IOT Device Activity', fields=activity_fields, filters=filters, order_by="creation desc", start=start, limit=limit)


def count_logs_by_company(company, filters=None):
	#frappe.logger(__name__).debug(_("query_device_logs_by_company {0}").format(company))
	filters = filters or {}
	filters.update({
		"owner_company": company
	})
	return frappe.db.count('IOT Device Activity', filters=filters)


def query_logs_by_device(sn, start=None, limit=None, filters=None):
	filters = filters or {}
	filters.update({
		"device": sn
	})
	return frappe.get_all('IOT Device Activity', fields=activity_fields, filters=filters, order_by="creation desc", start=start, limit=limit)


def count_logs_by_device(sn, filters=None):
	filters = filters or {}
	filters.update({
		"device": sn
	})
	return frappe.db.count('IOT Device Activity', filters=filters)