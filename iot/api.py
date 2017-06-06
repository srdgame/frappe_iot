# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import redis
import requests
import datetime
import uuid
from frappe.utils import now, get_datetime, convert_utc_to_user_timezone
from frappe import throw, msgprint, _, _dict
from iot.doctype.iot_hdb_settings.iot_hdb_settings import IOTHDBSettings
from hdb_api import list_iot_devices


def valid_auth_code(auth_code=None):
	auth_code = auth_code or frappe.get_request_header("AuthorizationCode")
	if not auth_code:
		throw(_("AuthorizationCode is required in HTTP Header!"))
	frappe.logger(__name__).debug(_("API AuthorizationCode as {0}").format(auth_code))

	user = frappe.get_value("IOT User Api", {"authorization_code": auth_code}, "user")
	if not user:
		throw(_("Authorization Code is incorrect!"))
	# form dict keeping
	form_dict = frappe.local.form_dict
	frappe.set_user(user)
	frappe.local.form_dict = form_dict


@frappe.whitelist(allow_guest=True)
def list_devices():
	valid_auth_code()
	return list_iot_devices(frappe.session.user)

