# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt
#
# You need to using the mqtt auth plugin from:
#  https://github.com/symgrid/mosquitto-auth-plug
#  which has improve on acl with device id instead of ful topic

from __future__ import unicode_literals
import frappe
import json
import hashlib
import hmac
import re
from frappe import throw, msgprint, _

match_topic = re.compile(r'^([^/]+)/(.+)$')


def get_post_json_data():
	if frappe.request.method != "POST":
		throw(_("Request Method Must be POST!"))
	ctype = frappe.get_request_header("Content-Type")
	if "json" not in ctype.lower():
		throw(_("Incorrect HTTP Content-Type found {0}").format(ctype))
	data = frappe.request.get_data()
	if not data:
		throw(_("JSON Data not found!"))
	return json.loads(data.decode('utf-8'))


def fire_raw_content(status=200, content="", content_type='text/plain'):
	"""
	I am hack!!!
	:param status: HTTP Status Code
	:param content: HTTP Response Content
	:param content_type: HTTP Response Content Type
	:return:
	"""
	frappe.response['http_status_code'] = status
	frappe.response['filename'] = ''
	frappe.response['filecontent'] = content
	frappe.response['content_type'] = content_type
	frappe.response['type'] = 'download'
	if status != 200:
		frappe.local.is_ajax = True
		raise frappe.AuthenticationError


def http_200ok(info=""):
	fire_raw_content(status=200, content=info)


def http_403(err):
	frappe.logger(__name__).debug(_("MQTT Auth V2 - 403 : {0}").format(err))
	fire_raw_content(status=403, content=err)


@frappe.whitelist(allow_guest=True)
def auth(clientid=None, username=None, password=None):
	clientid = clientid or frappe.form_dict.clientid
	username = username or frappe.form_dict.username
	password = password or frappe.form_dict.password

	frappe.logger(__name__).debug(_("MQTT Auth: client_id - {0} username - {1} password {2}").format(clientid, username, password))
	assert(clientid and username and password)

	if not frappe.local.site:
		return http_403("Auth Error - Site not created!")

	if username[0:4] == "dev=":
		index = username.rfind("|time=")
		if index == -1:
			return http_403("Auth Error - time is missing in username")
		device_id = username[4:index]
		timestamp = username[index+6:] #TODO: validate timestamp here
		sid = frappe.db.get_single_value("IOT HDB Settings", "mqtt_device_password_sid") or 'ZGV2aWNlIGlkCg=='
		encoded_password = timestamp
		try:
			encoded_password = hmac.new(sid.encode('utf-8'), username.encode('utf-8'), hashlib.sha1).hexdigest()
		except Exception as ex:
			frappe.logger(__name__).error(repr(ex))
			return http_403("Auth Error - hashing exception failure!")

		if clientid == device_id and password.lower() == encoded_password:
			if frappe.get_value("IOT Device", clientid, "enabled") == 1:
				return http_200ok()
			else:
				return http_403("Auth Error - Device is disabled!")
		else:
			return http_403("Auth Error - Device hashing password incorrect!")

	if username == 'root':
		root_password = frappe.db.get_single_value("IOT HDB Settings", "mqtt_root_password") or 'bXF0dF9pb3RfYWRtaW4K'
		if password == root_password:
			return http_200ok()
		else:
			return http_403("Auth Error - Root password incorrect")
	else:
		sid = frappe.db.get_single_value("IOT HDB Settings", "mqtt_device_password_sid") or 'ZGV2aWNlIGlkCg=='
		m = hashlib.md5()
		m.update(frappe.as_unicode(username + sid).encode('utf-8'))
		if password == m.hexdigest():
			# TODO: There is not more device will use this method for auth. TO BE REMOVED.
			if frappe.get_value("IOT Device", username, "enabled") == 1:
				return http_200ok()
			else:
				return http_403("Auth Error")
		else:
			try:
				# Valid user with session sid first.
				data = frappe.cache().hget("session", password)
				if data:
					if data.get('user') == username:
						return http_200ok()
					else:
						return http_403("Auth Error - Session not matching user")
				else:
					frappe.local.login_manager.authenticate(username, password)
					if frappe.local.login_manager.user == username:
						return http_200ok()
					else:
						return http_403("Auth Error - User/Password does not match")
			except Exception as ex:
				frappe.logger(__name__).error(repr(ex))
				return http_403("Auth Error - exception failure!")

	return http_403("Auth Error - what else")


@frappe.whitelist(allow_guest=True)
def superuser(username=None):
	username = username or frappe.form_dict.username
	frappe.logger(__name__).debug(_("MQTT Superuser: username - {0}").format(username))
	if username == "root":
		return http_200ok()
	else:
		return http_403("Auth Error")


@frappe.whitelist(allow_guest=True)
def acl(username=None, topic=None, clientid=None, access=None, acc=None):
	username = username or frappe.form_dict.username
	topic = topic or frappe.form_dict.topic			# via our auth plugin, this topic is the device id only
	clientid = clientid or frappe.form_dict.clientid
	acc = access or acc or frappe.form_dict.access or frappe.form_dict.acc
	frappe.logger(__name__).debug(_("MQTT Acl: username - {0} topic - {1} clientid - {2} acc - {3}").format(username, topic, clientid, acc))

	if username == 'root':
		return http_200ok()
	else:
		try:
			devid = topic
			sub = None
			g = match_topic.match(topic)
			if g:
				g = g.groups()
				devid = g[0]
				sub = g[1]
			else:
				return http_403("Auth Error - topic match error")

			if clientid == devid:
				return http_200ok()		# your self topics

			if username[0:4] == "dev=":
				return http_403("Auth Error - cannot find device name")

			dev = frappe.get_doc("IOT Device", devid)
			role = dev.get_role_permission(username)
			if role == 'Admin':
				return http_200ok()
			else:
				if sub == 'data' and role:
					return http_200ok()
				return http_403("Auth Error - user is not 'Admin'")
		except Exception as ex:
			frappe.logger(__name__).error(repr(ex))
			return http_403("Auth Error - exception")

	return http_403("Auth Error - Not here")


@frappe.whitelist(allow_guest=True)
def ping():
	return "mqtt_auth.pong"


