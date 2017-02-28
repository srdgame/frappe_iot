// Copyright (c) 2016, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT Device Bunch', {
	setup: function(frm) {
		frm.fields_dict["owner_type"].get_query = function(){
			return {
				filters: {
					"name": ["in","User,IOT Employee Group"],
				}
			};
		};
	},
	refresh: function(frm) {
		if (frm.fields_dict["owner_type"].val() == 'User') {
			frm.fields_dict["owner_id"].get_query = function () {
				return {
					filters: {"ignore_user_type": 1}
				};
			};
		} else {
			frm.fields_dict["owner_id"].get_query = null;
		}
	}
});
