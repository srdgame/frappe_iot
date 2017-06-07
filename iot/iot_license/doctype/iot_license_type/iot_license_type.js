// Copyright (c) 2017, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT License Type', {
	refresh: function(frm) {
		frappe.call({
			type: 'GET',
			method: "iot.iot_license.doctype.iot_license_type.iot_license_type.query_plugin_list",
			args: {
				"type": "IO Plugin"
			},
			callback: function (r, rt) {
				if (r.message) {
					frm.fields_dict['io_plugin_list'].df.options = r.message;
				}
			}
		});
		frappe.call({
			type: 'GET',
			method: "iot.iot_license.doctype.iot_license_type.iot_license_type.query_plugin_list",
			args: {
				"type": "DS Plugin"
			},
			callback: function (r, rt) {
				if (r.message) {
					frm.fields_dict['ds_plugin_list'].df.options = r.message;
				}
			}
		});
	}
});

frappe.ui.form.on('IOT License TypePlugin', {
	refresh: function(frm) {

	}
});
