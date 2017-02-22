from frappe import _

def get_data():
	return [
		{
			"label": _("Portal"),
			"items": [
				{
					"type": "doctype",
					"name": "IOT Homepage",
					"description": _("Settings for IOT Cloud homepage"),
				}
			]
		}
	]
