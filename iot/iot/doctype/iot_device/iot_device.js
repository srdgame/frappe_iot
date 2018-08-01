// Copyright (c) 2017, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT Device', {
	refresh: function(frm) {
		if (frm.doc.use_beta == 0 || !frm.doc.use_beta_start_time) {
			frm.add_custom_button(__("Enable Beta"), function () {
				frm.events.set_use_beta(frm);
			}).removeClass("btn-default").addClass("btn-warning");
		}
		if (frappe.user.has_role(['Administrator','IOT Manager'])) {
			frm.add_custom_button(__("Clean Activities"), function () {
				frm.events.clean_activities(frm);
			}).removeClass("btn-default").addClass("btn-warning");
			frm.add_custom_button(__("Clean Events"), function () {
				frm.events.clean_events(frm);
			}).removeClass("btn-default").addClass("btn-warning");
		}
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
	},
	clean_activities: function(frm) {
		return frappe.call({
			doc: frm.doc,
			method: "clean_activities",
			freeze: true,
			callback: function(r) {
				if(!r.exc) frm.refresh_fields();
			}
		})
	},
	clean_events: function(frm) {
		return frappe.call({
			doc: frm.doc,
			method: "clean_events",
			freeze: true,
			callback: function(r) {
				if(!r.exc) frm.refresh_fields();
			}
		})
	}
});
