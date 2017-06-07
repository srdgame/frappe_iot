# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class IOTLicenseType(Document):
	pass


@frappe.whitelist()
def query_plugin_list(type):
	plugins = [d.name for d in frappe.get_list("IOT License Plugin", fields=["name"], filters={"plugin_type": type})]
	return "\n".join(str(plugin) for plugin in plugins)
