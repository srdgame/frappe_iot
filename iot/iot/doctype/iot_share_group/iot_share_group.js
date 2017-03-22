// Copyright (c) 2017, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT Share Group', {
	setup: function(frm) {
		frm.fields_dict.devices.grid.get_field('device').get_query  = function(){
			return {
				filters: {"company": frm.doc.company}
			};
		};
		frm.fields_dict.devices.grid.get_field('user').get_query  = function(){
			return {
				filters: {"ignore_user_type": 1}
			};
		};
	},
	refresh: function(frm) {

	}
});
