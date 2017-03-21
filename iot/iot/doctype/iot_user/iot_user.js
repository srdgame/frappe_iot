// Copyright (c) 2016, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT User', {
	/*
	setup: function(frm) {
		frm.fields_dict["products"].grid.get_field("item_code").get_query = function(){
			return {
				filters: {'show_in_website': 1}
			}
		}
	},
	*/
	onload: function(frm) {
		if(has_common(roles, ["Administrator", "System Manager", "IOT Manager"]) && !frm.doc.__islocal) {
			if(!frm.group_editor) {
				var group_area = $('<div style="min-height: 300px">')
					.appendTo(frm.fields_dict.group_html.wrapper);
				frm.group_editor = new frappe.GroupEditor(frm, group_area);
			} else {
				frm.group_editor.refresh();
			}
		}
		frm.set_query("user", function() {
			return {
				"filters": {
					"ignore_user_type": 1,
				}
			};
		});
	},
	refresh: function(frm) {
		var doc = frm.doc;
		if(doc.name===user && !doc.__unsaved
			&& (doc.language || frappe.boot.user.language)
			&& doc.language !== frappe.boot.user.language) {
			msgprint(__("Refreshing..."));
			window.location.reload();
		}

		frm.toggle_display(['group_settings'], false);

		if(!doc.__islocal){
			if(has_common(roles, ["Administrator", "System Manager", "IOT Manager"])) {
				frm.toggle_display(['group_settings'], true);
			}
			frm.trigger('enabled');

			frm.group_editor && frm.group_editor.refresh();
		}

		if (frappe.route_flags.unsaved===1){
		    frm.dirty();
		}
	},
	enabled: function(frm) {
		var doc = frm.doc;
		if(!doc.__islocal && has_common(roles, ["Administrator", "System Manager", "IOT Manager"])) {
			frm.toggle_display(['group_settings'], true);
			frm.set_df_property('enabled', 'read_only', 0);
		}
	}
});


frappe.GroupEditor = Class.extend({
	init: function(frm, wrapper) {
		this.wrapper = $('<div class="row group-block-list"></div>').appendTo(wrapper);
		this.frm = frm;
		this.load_roles();
	},
	load_roles: function() {
		var enterprise = this.frm.doc.enterprise
		this.__org_enterprise = enterprise
		var me = this;
		var wrapper = this.wrapper;
		$(wrapper).html('<div class="help">' + __("Loading") + '...</div>')
		return frappe.call({
			method: 'frappe.client.get_list',
			args: {
				doctype: 'IOT Role'
			},
			callback: function(r) {
				me.roles = r.message;
				me.role_select = '<div class="control-input-wrapper">' +
					'<div class="control-input"><select data-doctype="IOT User" placeholder="" data-fieldname="role" data-fieldtype="Link" maxlength="140" class="input-with-feedback form-control" autocomplete="off" type="text">' +
					'<option value="New">New</option>' +
					'<option value="Open">Open</option>' +
					'<option value="Fixed">Fixed</option>' +
					'<option value="Closed">Closed</option>' +
					'</select></div>' +
					'<div class="control-value like-disabled-input" style="display: none;">New</div>' +
					'<p class="help-box small text-muted hidden-xs"></p>' +
					'</div>';
				alert(me.role_select);
				me.load_groups();
			}
		});
	},
	load_groups: function() {
		var enterprise = this.frm.doc.enterprise
		this.__org_enterprise = enterprise
		var me = this;
		var wrapper = this.wrapper;
		$(wrapper).html('<div class="help">' + __("Loading") + '...</div>')
		return frappe.call({
			method: 'iot.iot.doctype.iot_enterprise.iot_enterprise.get_groups',
			args: {enterprise: enterprise},
			callback: function(r) {
				me.groups = r.message;
				me.make();
				me.refresh();
			}
		});
	},
	make: function() {
		var me = this;
		var wrapper = this.wrapper;
		$(wrapper).html('')
		me.groups.forEach(function(m) {
			$(repl('<div class="col-sm-6" title="%(desc)s"><div class="checkbox">\
				<label><input type="checkbox" class="block-group-check" data-group="%(group)s">\
				%(name)s</label></div>%(role_select)s</div>', {group: m.name, name: m.grp_name, desc:m.description, role_select:me.role_select})).appendTo(me.wrapper);
		});
		this.bind();
	},
	refresh: function() {
		// Check whether the Enterprise changed or not
		var enterprise = this.frm.doc.enterprise
		if(enterprise != this.__org_enterprise) {
			// reload the groups when Enterprise has changed
			this.load_groups();
		} else {
			var me = this;
			this.wrapper.find(".block-group-check").prop("checked", false);
			$.each(this.frm.doc.group_assigned, function(i, d) {
				me.wrapper.find(".block-group-check[data-group='"+ d.group +"']").prop("checked", true);
			});
		}
	},
	bind: function() {
		// Do not binded twice or change event will be called more than once
		if(this.__wrapper_binded) {
			return;
		}
		this.__wrapper_binded = true;
		this.wrapper.on("change", ".block-group-check", function() {
			var group = $(this).attr('data-group');
			if($(this).prop("checked")) {
				// Make sure the group is not assigned twice!
				me.frm.doc.group_assigned = $.map(me.frm.doc.group_assigned || [], function(d) { if(d.group != group){ return d } });
				me.frm.add_child("group_assigned", {"group": group});
			} else {
				// remove from group_assigned
				me.frm.doc.group_assigned = $.map(me.frm.doc.group_assigned || [], function(d) { if(d.group != group){ return d } });
			}
		});
	}
});
