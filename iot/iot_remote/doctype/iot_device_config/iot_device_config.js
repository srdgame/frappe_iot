// Copyright (c) 2017, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT Device Config', {
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
