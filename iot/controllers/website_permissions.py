# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils.user import is_website_user


def has_website_permission(doc, ptype, user, verbose=False):
	return False
