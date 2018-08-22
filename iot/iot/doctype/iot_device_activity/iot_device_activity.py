# -*- coding: utf-8 -*-
# Copyright (c) 2018, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import requests
from frappe import _,throw
from frappe.model.document import Document
from frappe.utils import get_fullname, now, get_datetime_str

class IOTDeviceActivity(Document):
	def before_insert(self):
		self.full_name = get_fullname(self.user)

	# def after_insert(self):
	# 	self.insert_to_influxdb()
	#
	# def insert_to_influxdb(self):
	# 	from iot.iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings
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


def add_device_owner_log(subject, dev_name, dev_company, owner_type=None, owner_id=None, status="Success"):
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


def clear_device_activity_logs():
	"""clear 100 day old iot device activities"""
	frappe.db.sql("""delete from `tabIOT Device Activity` where creation<DATE_SUB(NOW(), INTERVAL 100 DAY)""")


def query_logs_by_user(user, start=None, limit=None):
	from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups
	groups = [g.name for g in list_user_groups(user)]
	groups.append(user)
	return frappe.get_all('IOT Device Activity', fields='*', filters={"owner_id": ["in", groups]}, order_by="creation desc", start=start, limit=limit)


def count_logs_by_user(user):
	from cloud.cloud.doctype.cloud_company_group.cloud_company_group import list_user_groups
	groups = [g.name for g in list_user_groups(user)]
	groups.append(user)
	return frappe.db.count('IOT Device Activity', filters={"owner_id": ["in", groups]})


def query_logs_by_company(company, start=None, limit=None):
	#frappe.logger(__name__).debug(_("query_device_logs_by_company {0}").format(company))
	return frappe.get_all('IOT Device Activity', fields='*', filters={"owner_company": company}, order_by="creation desc", start=start, limit=limit)


def count_logs_by_company(company, start=None, limit=None):
	#frappe.logger(__name__).debug(_("query_device_logs_by_company {0}").format(company))
	return frappe.db.count('IOT Device Activity', filters={"owner_company": company})


def query_logs_by_device(sn, start=None, limit=None):
	return frappe.get_all('IOT Device Activity', fields='*', filters={"device": sn}, order_by="creation desc", start=start, limit=limit)


def count_logs_by_device(sn):
	return frappe.db.count('IOT Device Activity', filters={"device": sn})