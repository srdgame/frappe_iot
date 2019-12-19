# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("IOT"),
			"items": [
				{
					"type": "doctype",
					"name": "IOT Device",
					"onboard": 1,
					"description": _("IOT Device"),
				},
				{
					"type": "doctype",
					"name": "IOT Virtual Device",
					"onboard": 1,
					"description": _("IOT Virtual Device"),
				},
				{
					"type": "doctype",
					"name": "IOT Device Share",
					"onboard": 1,
					"description": _("IOT Device Share"),
				},
				{
					"type": "doctype",
					"name": "IOT Share Group",
					"onboard": 1,
					"description": _("IOT Share Group"),
				},
				{
					"type": "doctype",
					"name": "IOT Batch Task",
					"onboard": 1,
					"description": _("IOT Batch Task"),
				}
			]
		},
		{
			"label": _("IOT Events"),
			"items": [
				{
					"type": "doctype",
					"name": "IOT Device Event",
					"onboard": 1,
					"description": _("IOT Device Event"),
				},
				{
					"type": "doctype",
					"name": "IOT Device Activity",
					"onboard": 1,
					"description": _("IOT Device Activity"),
				},
			]
		},
		{
			"label": _("IOT Settings"),
			"items": [
				{
					"type": "doctype",
					"name": "IOT HDB Settings",
					"onboard": 1,
					"description": _("IOT HDB Settings"),
				},
				{
					"type": "doctype",
					"name": "IOT User Api",
					"onboard": 1,
					"description": _("IOT User Api"),
				}
			]
		}
	]
