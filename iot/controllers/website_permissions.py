# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils.user import is_website_user


def has_website_permission(doc, ptype, user, verbose=False):
	return False
