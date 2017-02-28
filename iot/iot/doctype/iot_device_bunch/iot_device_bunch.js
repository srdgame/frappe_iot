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
		frm.fields_dict["owner_type"].on("change", function() {
			this.change_owner_type(frm);
		});
	},
	refresh: function(frm) {

	},
	change_owner_type: function(frm) {
		alert(frm.fields_dict["owner_type"].value);
		if (frm.fields_dict["owner_type"].value == 'User') {
			frm.fields_dict["owner_id"].get_query = function () {
				return {
					filters: {"ignore_user_type": 1}
				};
			};
		} else {
			frm.fields_dict["owner_id"].get_query = null;
		}
	},
});
