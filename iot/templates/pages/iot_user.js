frappe.ready(function() {
	$(".btn-iot-delete-user").click(function() {
		var args = {
			enterprise: $("#enterprise").val(),
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
					strength_message.addClass('hidden');
					if(r.message) {
						frappe.msgprint(r.message);
						setTimeout(function() {
							window.location.href = "/iot_users/"+args.user;
						}, 2000);
					}
				} else {
					strength_message.removeClass('hidden');
					strength_message.text(r.message);
				}
			}
		});

        return false;
	});

	window.strength_message = $('.iot-delete-user-strength-message');
});