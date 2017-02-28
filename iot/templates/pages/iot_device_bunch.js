frappe.ready(function() {
	$(".btn-enable-iot").click(function() {
		var args = {
			bunch_name: $("#bunch_name").val(),
			code: $("#code").val(),
			owner_type: $("#owner_type").val(),
			owner_id: $("#owner_id").val()
		};

		if(!args.bunch_name) {
			frappe.msgprint("Bunch Code Name Required.");
			return false;
		}
		if(!args.code) {
			frappe.msgprint("Bunch Code Required.");
			return false;
		}

		frappe.call({
			type: "POST",
			method: "iot.iot.doctype.iot_device_bunch.iot_device_bunch.add_bunch_code",
			btn: $(".btn-enable-iot"),
			args: args,
			statusCode: {
				401: function() {
					$('.page-card-head .indicator').removeClass().addClass('indicator red')
						.text(__('Invalid Bunch Code'));
				},
				200: function(r) {
					$("input").val("");
					strength_indicator.addClass('hidden');
					strength_message.addClass('hidden');
					$('.page-card-head .indicator')
						.removeClass().addClass('indicator green')
						.html(__('Bunch Code Inserted'));
					if(r.message) {
						frappe.msgprint(__("Bunch Code Inserted"));
	                    setTimeout(function() {
							window.location.href = "/iot_me";
	                    }, 2000);
					}
				}
			}
		});

        return false;
	});

	window.strength_indicator = $('.bunch-code-strength-indicator');
	window.strength_message = $('.bunch-code-strength-message');
});