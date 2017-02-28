# -*- coding: utf-8 -*-
# Copyright (c) 2015, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class IOTDeviceBunch(Document):
	def has_website_permission(self, ptype, verbose=False):
		"""Returns true if current user is the session user"""
		return self.owner_type == "User" and self.owner_id == frappe.session.user
