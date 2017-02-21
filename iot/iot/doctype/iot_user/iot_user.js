// Copyright (c) 2016, Dirk Chang and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT User', {
	onload: function(frm) {
		if(has_common(user_roles, ["Administrator", "System Manager", "IOT Manager"]) && !frm.doc.__islocal) {
			if(!frm.group_editor) {
				var group_area = $('<div style="min-height: 300px">')
					.appendTo(frm.fields_dict.groups_html.wrapper);
				frm.group_editor = new frappe.GroupEditor(frm, group_area)
			} else {
				frm.group_editor.show();
			}
		}
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
			if(has_common(user_roles, ["Administrator", "System Manager", "IOT Manager"])) {
				frm.toggle_display(['group_settings'], true);
			}
			frm.trigger('enabled');

			frm.group_editor && frm.group_editor.refresh();
		}

		if (frappe.route_flags.unsaved===1){
		    cur_frm.dirty();
		}
	},
	enabled: function(frm) {
		var doc = frm.doc;
		if(!doc.__islocal && has_common(user_roles, ["Administrator", "System Manager", "IOT Manager"])) {
			frm.toggle_display(['group_settings'], doc.enabled);
			frm.set_df_property('enabled', 'read_only', 0);
		}
	}
});


frappe.GroupEditor = Class.extend({
	init: function(frm, wrapper) {
		this.wrapper = $('<div class="row group-block-list"></div>').appendTo(wrapper);
		this.frm = frm;
		this.load_groups(this.frm.doc.enterprise);
	},
	load_groups: function(enterprise) {
		var me = this;
		var wrapper = this.wrapper;
		$(wrapper).html('<div class="help">' + __("Loading") + '...</div>')
		return frappe.call({
			method: 'iot.iot.doctype.iot_user.iot_user.get_all_groups',
			args: {enterprise: enterprise},
			callback: function(r) {
				me.groups = r.message;
				me.make();

				// refresh call could've already happened
				// when all role checkboxes weren't created
				if(cur_frm.doc) {
					cur_frm.group_editor.show();
				}
			}
		});
    },
	make: function() {
		var me = this;
		me.groups.forEach(function(m) {
			$(repl('<div class="col-sm-6"><div class="checkbox">\
				<label><input type="checkbox" class="block-group-check" data-group="%(group)s">\
				%(group)s</label></div></div>', {group: m})).appendTo(me.wrapper);
		});
		this.bind();
	},
	refresh: function() {
		var me = this;
		this.wrapper.find(".block-group-check").prop("checked", true);
		$.each(this.frm.doc.group_assigned, function(i, d) {
			me.wrapper.find(".block-group-check[data-group='"+ d.group +"']").prop("checked", false);
		});
	},
	bind: function() {
		this.wrapper.on("change", ".block-group-check", function() {
			var group = $(this).attr('data-group');
			if($(this).prop("checked")) {
				// remove from group_assigned
				me.frm.doc.group_assigned = $.map(me.frm.doc.group_assigned || [], function(d) { if(d.group != group){ return d } });
			} else {
				me.frm.add_child("group_assigned", {"group": group});
			}
		});
	}
});
