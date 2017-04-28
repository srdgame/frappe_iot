// Copyright (c) 2017, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT Device Error', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 1 && frm.doc.wechat_notify == 1) {
			frm.add_custom_button(__("Fire Wechat Notify"), function() {
				 frm.events.wechat_msg_send(frm);
			}).removeClass("btn-default").addClass("btn-primary");;
		}
	},
	wechat_msg_send: function(frm) {
		return frappe.call({
			doc: frm.doc,
			method: "wechat_msg_send",
			freeze: true,
			callback: function(r)  {
				if(r.exc) {
					if(r._server_messages)
						frappe.msgprint(r._server_messages);
				} else {
					frappe.msgprint(__("Resend Successfully"));
				}
			}
		})
	}
});
