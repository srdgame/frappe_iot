frappe.provide("iot.setup");

frappe.pages['setup-wizard'].on_page_load = function(wrapper) {
	if(frappe.sys_defaults.company) {
		frappe.set_route("desk");
		return;
	}
};

frappe.setup.on("before_load", function () {
	iot.setup.slides_settings.map(frappe.setup.add_slide);
});

iot.setup.slides_settings = [
	{
		// IOT
		name: 'iot',
		icon: "fa fa-bookmark",
		title: __("IOT"),
		// help: __('Default HDB Settings.'),
		fields: [
			{
				fieldname: 'hdb_authorization_code',
				label: __('HDB Authorization Code'),
				fieldtype: 'Data',
				reqd: 1
			},
			{
				fieldname: 'hdb_user',
				label: __('HDB User'),
				fieldtype: 'Data',
				reqd: 1
			},
			{
				fieldname: 'hdb_redis_server',
				label: __('Redis Server'),
				fieldtype: 'Data',
				reqd: 1
			},
			{
				fieldname: 'hdb_influxdb_server',
				label: __('InfluxDB Server'),
				fieldtype: 'Data',
				reqd: 1
			},
			{
				fieldname: 'hdb_mqtt_root_password',
				label: __('MQTT Root Password'),
				fieldtype: 'Data',
				reqd: 1
			},
			{
				fieldname: 'hdb_device_password_sid',
				label: __('MQTT Device Password SID'),
				fieldtype: 'Data'
			}
		]
	}
];
