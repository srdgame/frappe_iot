frappe.ready(function() {
	$(".btn-iot-delete-user").click(function() {
		var args = {
			company: $("#company").val(),
			user: $("#user").val(),
		};

		if(!args.user) {
			frappe.msgprint("User Required.");
			return false;
		}

		frappe.call({
			type: "POST",
			method: "iot.iot.doctype.iot_user.iot_user.delete_user",
			btn: $(".btn-iot-delete-user"),
			args: args,
			callback: function(r) {
				if(!r.exc) {
					if(r.message) {
						frappe.msgprint(r.message);
						setTimeout(function() {
							window.location.href = "/iot_companies/"+args.company;
						}, 2000);
					}
				}
			}
		});

        return false;
	});
});