// Copyright (c) 2017, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT Device', {
	refresh: function(frm) {
		frm.add_custom_button(__("Enable Beta"), function() {
			frm.events.set_use_beta(frm);
		}).removeClass("btn-default").addClass("btn-warning");
	},
	set_use_beta: function(frm) {
		return frappe.call({
			doc: frm.doc,
			method: "set_use_beta",
			freeze: true,
			callback: function(r) {
				if(!r.exc) frm.refresh_fields();
			}
		})
	}
});
