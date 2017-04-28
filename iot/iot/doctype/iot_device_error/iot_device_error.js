// Copyright (c) 2017, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT Device Error', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 1 && frm.doc.wechat_notify == 1) {
			frm.add_custom_button(__("Resend"), function() {
				 frm.events.resend_wechat_msg(frm);
			});
		}
	},
	resend_wechat_msg: function(frm) {
		return frappe.call({
			doc: frm.doc,
			method: "resend_wechat_msg",
			freeze: true,
			callback: function(r)  {
				if(r.exc) {
					if(r._server_messages)
						frappe.msgprint(r._server_messages);
				} else {
					frappe.msgprint(r.message);
				}
			}
		})
	}
});
