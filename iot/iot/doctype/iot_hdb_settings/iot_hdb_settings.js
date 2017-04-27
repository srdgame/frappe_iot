// Copyright (c) 2016, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT HDB Settings', {
	setup: function(frm) {
		frm.events.refresh_status(frm);
	},
	refresh: function(frm) {
		frm.add_custom_button(__("Refresh Server Status"), function() {
			frm.events.refresh_status(frm);
		}).removeClass("btn-default").addClass("btn-primary");

		var grid_html = '<div class="form-group"> \
							<div class="clearfix"> \
								<label class="control-label" style="padding-right: 0px;">%(title)s</label> \
							</div> \
							<div class="control-input-wrapper"> \
								<img height="32px" src="/assets/iot/images/connect/%(status)s.png"> \
							</div> \
						</div>'

		var redis_status = frm.doc.redis_status  || 'none';
		var influxdb_status = frm.doc.influxdb_status  || 'none';
		var hdb_status = frm.doc.hdb_status  || 'none';
		var s = $(repl(grid_html, {title: __("Redis"), status: redis_status.toLowerCase()}));
		$(frm.fields_dict['server_status_html'].wrapper).html(s);
		var s = $(repl(grid_html, {title: __("InfluxDB"), status: influxdb_status.toLowerCase()}));
		$(frm.fields_dict['server_status_html'].wrapper).append(s);
		var s = $(repl(grid_html, {title: __("HDB"), status: hdb_status.toLowerCase()}));
		$(frm.fields_dict['server_status_html'].wrapper).append(s);
	},
	refresh_status: function(frm) {
		return frappe.call({
			doc: frm.doc,
			method: "refresh_status",
			freeze: true,
			callback: function(r) {
				if(!r.exc) frm.reload_doc();
			}
		})
	}
});
