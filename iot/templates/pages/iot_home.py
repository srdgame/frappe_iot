# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

no_cache = 1
no_sitemap = 1

def get_context(context):
	homepage = frappe.get_doc('IOT Homepage')

	context.title = homepage.title or homepage.company

	context.homepage = homepage
