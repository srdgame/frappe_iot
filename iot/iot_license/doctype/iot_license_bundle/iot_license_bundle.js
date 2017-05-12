// Copyright (c) 2017, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT License Bundle', {
	setup: function(frm) {
		frm.fields_dict["source_type"].get_query = function(){
			return {
				filters: {
					"name": ["in","Stock Order,Cloud Company,User"]
				}
			}
		};
	},
	refresh: function(frm) {

	}
});
