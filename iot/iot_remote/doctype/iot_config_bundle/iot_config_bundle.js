// Copyright (c) 2017, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT Config Bundle', {
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

	},
	batch_add: function(frm) {
		if (frm.doc.bunch_code) {
			frappe.call({
				type: "GET",
				method: 'frappe.client.get_list',
				args: {
					doctype: "IOT Device",
					filters: {
						"bunch": frm.doc.bunch_code
					},
					fields: ["sn", "dev_name"]
				},
				callback: function (r) {
					var devices = frm.doc.devices;
					if (r.message) {
						$.each(r.message, function (i, d) {
							if (! $.map(devices || [], function(dev) { if(dev.device == d.sn){ return dev } })[0]) {
								var row = frappe.model.add_child(cur_frm.doc, "IOT Config BundleDevice", "devices");
								row.device = d.sn;
								row.device_name = d.dev_name;
							}
						});
					}
					refresh_field("devices");
				}
			});
		}
	}
});

frappe.ui.form.on('IOT Config BundleDevice', {
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
