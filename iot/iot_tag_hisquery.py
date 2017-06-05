# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals
import frappe
import datetime
import time
import redis
import requests
from frappe.utils import now, get_datetime, convert_utc_to_user_timezone
from iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings


UTC_FORMAT1 = "%Y-%m-%dT%H:%M:%S.%fZ"
UTC_FORMAT2 = "%Y-%m-%dT%H:%M:%SZ"


def utc2local(utc_st):
	now_stamp = time.time()
	local_time = datetime.datetime.fromtimestamp(now_stamp)
	utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
	offset = local_time - utc_time
	local_st = utc_st + offset
	return local_st


@frappe.whitelist()
def ping():
	return "Pong"


@frappe.whitelist()
def taghisdata(sn=None, vsn=None, fields=None, condition=None):
	vsn = vsn or sn
	fields = fields or "*"
	doc = frappe.get_doc('IOT Device', sn)
	doc.has_permission("read")

	inf_server = IOTHDBSettings.get_influxdb_server()
	if not inf_server:
		frappe.logger(__name__).error("InfluxDB Configuration missing in IOTHDBSettings")
		return 500
	query = 'SELECT ' + fields + ' FROM "' + vsn + '"'
	if condition:
		query = query + " WHERE " + condition
	else:
		query = query + " LIMIT 1000"

	domain = frappe.get_value("Cloud Company", doc.company, "domain")
	r = requests.session().get(inf_server + "/query", params={"q": query, "db": domain}, timeout=10)
	if r.status_code == 200:
		try:
			res = r.json()["results"][0]['series'][0]['values']
			taghis = []
			for i in range(0, len(res)):
				hisvalue = {}
				#print('*********', res[i][0])
				try:
					utc_time = datetime.datetime.strptime(res[i][0], UTC_FORMAT1)
				except Exception as err:
					pass
				try:
					utc_time = datetime.datetime.strptime(res[i][0], UTC_FORMAT2)
				except Exception as err:
					pass
				#local_time = utc2local(utc_time).strftime("%Y-%m-%d %H:%M:%S")
				local_time = str(convert_utc_to_user_timezone(utc_time).replace(tzinfo=None))
				#print('#######', local_time)
				if res[i][2] == '1':
					hisvalue = {'name': res[i][1], 'value': res[i][4], 'time': local_time, 'quality': 0}
				elif res[i][2] == '2':
					hisvalue = {'name': res[i][1], 'value': res[i][3], 'time': local_time, 'quality': 0}
				taghis.append(hisvalue)
			#print(taghis)
			return taghis
		except Exception as err:
			return r.json()


@frappe.whitelist()
def iot_device_tree(sn=None):
	sn = sn or frappe.form_dict.get('sn')
	doc = frappe.get_doc('IOT Device', sn)
	doc.has_permission("read")
	client = redis.Redis.from_url(IOTHDBSettings.get_redis_server() + "/1")
	return client.lrange(sn, 0, -1)

