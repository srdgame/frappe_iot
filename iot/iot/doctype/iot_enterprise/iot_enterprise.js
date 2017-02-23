// Copyright (c) 2016, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT Enterprise', {
	setup: function(frm) {
		frm.fields_dict["user"].get_query = function(){
			return {
				filters: {"ignore_user_type": 1}
			}
		}
	},
	refresh: function(frm) {

	}
});
