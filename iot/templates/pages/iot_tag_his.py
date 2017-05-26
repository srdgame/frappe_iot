# coding=utf-8
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from iot.hdb import iot_device_tree

def get_context(context):
    if frappe.session.user == 'Guest':
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect
    context.no_cache = 1

    context.tag = frappe.form_dict.tag
    context.sn = frappe.form_dict.sn
    context.vsn = frappe.form_dict.vsn