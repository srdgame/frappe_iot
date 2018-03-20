// Copyright (c) 2018, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT Batch Task', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 1) {
			frm.add_custom_button(__("Resend"), function() {
				me.frm.set_value("status", "New");
				me.frm.amend_doc();
			});
		}
	}
});
