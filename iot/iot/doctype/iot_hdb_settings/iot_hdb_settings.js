// Copyright (c) 2016, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT HDB Settings', {
	refresh: function(frm) {
	},
	refresh_status: function(frm) {
		return frappe.call({
			doc: frm.doc,
			method: "refresh_status",
			freeze: true,
			callback: function(r) {
				if(!r.exc) frm.refresh_fields();
			}
		})
	}
});
