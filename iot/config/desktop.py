# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "IOT",
			"color": "#B8860B",
			"icon": "fa fa-cloud",
			"type": "module",
			"label": _("IOT")
		},
		{
			"module_name": "IOT Hub",
			"color": "#B8860B",
			"icon": "fa fa-cloud",
			"type": "module",
			"label": _("IOT Hub")
		}
	]
