# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json


def get_context(context):
	user_roles = frappe.get_roles(frappe.session.user)
	if 'IOT User' not in user_roles or frappe.session.user == 'Guest':
		raise frappe.PermissionError
		
	context.no_cache = 1
	context.show_sidebar = True
	device = frappe.get_doc('IOT Device', frappe.form_dict.sn)

	device.has_permission('read')

	context.doc = device


def get_tasks(project, start=0, search=None, item_status=None):
	filters = {"project": project}
	if search:
		filters["subject"] = ("like", "%{0}%".format(search))
	# if item_status:
# 		filters["status"] = item_status
	tasks = frappe.get_all("Task", filters=filters,
		fields=["name", "subject", "status", "_seen", "_comments", "modified", "description"],
		limit_start=start, limit_page_length=10)

	for task in tasks:
		task.todo = frappe.get_all('ToDo',filters={'reference_name':task.name, 'reference_type':'Task'},
		fields=["assigned_by", "owner", "modified", "modified_by"])

		if task.todo:
			task.todo=task.todo[0]
			task.todo.user_image = frappe.db.get_value('User', task.todo.owner, 'user_image')

		
		task.comment_count = len(json.loads(task._comments or "[]"))

		task.css_seen = ''
		if task._seen:
			if frappe.session.user in json.loads(task._seen):
				task.css_seen = 'seen'

	return tasks

@frappe.whitelist()
def get_task_html(project, start=0, item_status=None):
	return frappe.render_template("erpnext/templates/includes/projects/project_tasks.html",
		{"doc": {
			"name": project,
			"project_name": project,
			"tasks": get_tasks(project, start, item_status=item_status)}
		}, is_path=True)

def get_timesheets(project, start=0, search=None):
	filters = {"project": project}
	if search:
		filters["activity_type"] = ("like", "%{0}%".format(search))

	timesheets = frappe.get_all('Timesheet Detail', filters=filters,
	fields=['project','activity_type','from_time','to_time','parent'],
	limit_start=start, limit_page_length=10)
	for timesheet in timesheets:
		timesheet.infos = frappe.get_all('Timesheet', filters={"name": timesheet.parent},
			fields=['name','_comments','_seen','status','modified','modified_by'],
			limit_start=start, limit_page_length=10)

		for timesheet.info in timesheet.infos:
			timesheet.info.user_image = frappe.db.get_value('User', timesheet.info.modified_by, 'user_image')

			timesheet.info.comment_count = len(json.loads(timesheet.info._comments or "[]"))

			timesheet.info.css_seen = ''
			if timesheet.info._seen:
				if frappe.session.user in json.loads(timesheet.info._seen):
					timesheet.info.css_seen = 'seen'		
	return timesheets

@frappe.whitelist()
def get_timesheet_html(project, start=0):
	return frappe.render_template("erpnext/templates/includes/projects/project_timesheets.html",
		{"doc": {"timesheets": get_timesheets(project, start)}}, is_path=True)

