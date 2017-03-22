// Copyright (c) 2016, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT Device Bunch', {
	setup: function(frm) {
		/* frm.fields_dict["owner_type"].get_query = function(){
			return {
				filters: {
					"name": ["in","User,Cloud Company Group"]
				}
			}
		}; */
		frm.fields_dict["owner_id"].get_query = function(){
			if (frm.fields_dict["owner_type"].value === "User") {
				return {
					filters: {"ignore_user_type": 1}
				};
			} else {
				return {};
			}
		};
	},
	refresh: function(frm) {

	}
});
