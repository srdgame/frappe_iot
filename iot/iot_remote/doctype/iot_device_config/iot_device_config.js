// Copyright (c) 2017, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT Device Config', {
	setup: function(frm) {
		frm.fields_dict["file"].get_query = function(doc){
			return {
				filters: {"group": doc.group}
			};
		};
		frm.fields_dict["devices"].grid.get_field("device").get_query = function(doc, cdt, cdn) {
			//var d  = locals[cdt][cdn];
			return {
				query: "iot.iot_remote.doctype.iot_device_config.iot_device_config.query_device",
				filters: {
					"group": doc.group
				}
			};
		};
	},
	refresh: function(frm) {

	}
});
