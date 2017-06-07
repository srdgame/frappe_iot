// Copyright (c) 2017, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT License Type', {
	refresh: function(frm) {
		// frappe.call({
		// 	type: 'GET',
		// 	method: "iot.iot_license.doctype.iot_license_type.iot_license_type.query_plugin_list",
		// 	args: {
		// 		"type": "IO Plugin"
		// 	},
		// 	callback: function (r, rt) {
		// 		if (r.message) {
		// 			// frappe.meta.get_docfield('Child Table Name', 'field_name', cur_frm.doc.name).options = ['', 'Option 1', 'Option 2', 'Option 3'];
		// 			// cur_frm.refresh_field('child_table_field_name');
		// 			//
		//
		// 			var df = frappe.meta.get_docfield('IOT License TypePlugin', 'plugin', frm.doc.name);
		// 			df.options = r.message;
		// 			df.default = r.message.split("\n")[0];
		// 			//frm.refresh_field('io_plugin_list');
		//
		// 			// var df = frappe.meta.get_docfield('io_plugin_list', "plugin", frm.doc.name);
		// 			// df.options = r.message;
		// 			// df.default = r.message.split("\n")[0];
		// 			// frm.refresh_field('io_plugin_list');
		// 		}
		// 	}
		// });
		// frappe.call({
		// 	type: 'GET',
		// 	method: "iot.iot_license.doctype.iot_license_type.iot_license_type.query_plugin_list",
		// 	args: {
		// 		"type": "DS Plugin"
		// 	},
		// 	callback: function (r, rt) {
		// 		if (r.message) {
		// 			//frm.fields_dict['ds_plugin_list'].df.options = r.message;
		// 		}
		// 	}
		// });
	}
});
