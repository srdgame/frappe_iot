# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _


def get_context(context):

	context.no_cache = 1
	context.show_sidebar = True

	context.doc = {
		'name': 'Test baidu map',
	}
