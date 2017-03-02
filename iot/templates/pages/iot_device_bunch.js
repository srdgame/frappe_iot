frappe.ready(function() {
	$(".btn-add-bunch-code").click(function() {
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
			btn: $(".btn-add-bunch-code"),
			args: args,
			callback: function(r) {
				if(!r.exc) {
					$("input").val("");
					strength_indicator.addClass('hidden');
					strength_message.addClass('hidden');
					$('.page-card-head .indicator')
						.removeClass().addClass('indicator green')
						.html(__('Bunch Code Inserted'))
					if(r.message) {
						frappe.msgprint(r.message);
						setTimeout(function() {
							window.location.href = r.message;
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

	window.strength_indicator = $('.bunch-code-strength-indicator');
	window.strength_message = $('.bunch-code-strength-message');
});