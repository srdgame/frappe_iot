# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils.user import is_website_user


def after_insert(doc, method):
	doc.add_roles('IOT User')