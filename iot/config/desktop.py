# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "IOT",
			"label": _("IOT"),
			"color": "#B8860B",
			"icon": "fa fa-cloud",
			"type": "module"
		},
		{
			"module_name": "IOT Hub",
			"label": _("IOT Hub"),
			"color": "#B8860B",
			"icon": "fa fa-cloud",
			"type": "module"
		}
	]
