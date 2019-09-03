# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("IOT Hub"),
			"items": [
				{
					"type": "doctype",
					"name": "IOT User Application",
					"onboard": 1,
					"description": _("IOT User Application"),
				}
			]
		},
		{
			"label": _("IOT Portal"),
			"items": [
				{
					"type": "doctype",
					"name": "IOT Homepage",
					"onboard": 1,
					"description": _("Settings for IOT Cloud homepage"),
				}
			]
		}
	]
