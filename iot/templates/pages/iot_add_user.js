frappe.ready(function() {
	$(".btn-iot-add-user").click(function() {
		var args = {
			enable: $("#enable").val(),
			company: $("#company").val(),
			user: $("#user").val(),
		};

		if(!args.user) {
			frappe.msgprint("User Email Required.");
			return false;
		}

		frappe.call({
			type: "POST",
			method: "iot.iot.doctype.iot_user.iot_user.add_user",
			btn: $(".btn-iot-add-user"),
			args: args,
			callback: function(r) {
				if(!r.exc) {
					$("input").val("");
					strength_message.addClass('hidden');
					$('.page-card-head .indicator')
						.removeClass().addClass('indicator green')
						.html(__('User has been added'));
					if(r.message) {
						frappe.msgprint(r.message);
						setTimeout(function() {
							window.location.href = "/iot_users/"+args.user;
						}, 2000);
					}
				} else {
					$('.page-card-head .indicator').removeClass().addClass('indicator red')
					.text(r.message);
				}
			}
		});

        return false;
	});

	window.strength_message = $('.iot-add-user-strength-message');
});