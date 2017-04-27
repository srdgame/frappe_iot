# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _


def get_context(context):

	# context.no_cache = 1
	context.show_sidebar = True

	context.title = _("IOT Devices Map")
	context.doc = {
		'name': _("IOT Devices Map")
	}
