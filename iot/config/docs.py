"""
Configuration for docs
"""

# source_link = "https://github.com/[org_name]/iot"
# docs_base_url = "https://[org_name].github.io/iot"
# headline = "App that does everything"
# sub_heading = "Yes, you got that right the first time, everything"

def get_context(context):
	context.brand_html = ('<img class="brand-logo" src="'+context.docs_base_url
		+'/assets/img/frappe-bird-white.png"> Frappé Framework</img>')
	context.top_bar_items = [
		{"label": "IOT Enterprise", "url": context.docs_base_url + "/iot_enterprises", "right": 1},
		{"label": "IOT Devices", "url": context.docs_base_url + "/iot_devices", "right": 1},
		{"label": "IOT Account", "url": context.docs_base_url + "/iot_me", "right": 1},
		{"label": "SymLink", "url": 'https://symid.com', "right": 1}
	]
