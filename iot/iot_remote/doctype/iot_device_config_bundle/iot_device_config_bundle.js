// Copyright (c) 2017, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT Device Config Bundle', {
	setup: function(frm) {
		frm.fields_dict['config_file'].get_query  = function(doc){
			return {
				filters: {
					"config": doc.config
				}
			};
		};
	},
	refresh: function(frm) {

	}
});

frappe.ui.form.on('IOT Device Config BundleDevice', {
	device: function (doc, cdt, cdn) {
		var d = locals[cdt][cdn];
		frappe.call({
			type: "GET",
			method: "frappe.client.get",
			args: {
				doctype: "IOT Device",
				name: d.device,
			},
			callback: function(r, rt) {
				if(r.message) {
					frappe.model.set_value(cdt, cdn, "device_name", r.message.dev_name);
				}
			}
		});
	}
});