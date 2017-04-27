# -*- coding: utf-8 -*-
# Copyright (c) 2017, Dirk Chang and contributors
# For license information, please see license.txt

from __future__ import unicode_literals


def after_insert(doc, method):
	doc.add_roles('IOT User')

