
frappe.ready(function() {
	$("#reset-password").on("submit", function() {
		return false;
	});

	$("#new_password").on("keypress", function(e) {
		if(e.which===13) $("#update").click();
	});

	$("#update").click(function() {
		var args = {
			new_password: $("#new_password").val()
		};

		if(!args.new_password) {
			frappe.msgprint("New Password Required.")
			return;
		}

		frappe.call({
			type: "POST",
			method: "frappe.core.doctype.user.user.update_password",
			btn: $("#update"),
			args: args,
			statusCode: {
				401: function() {
					$('.page-card-head .indicator').removeClass().addClass('indicator red')
						.text(__('Invalid Password'));
				},
				200: function(r) {
					$("input").val("");
					strength_indicator.addClass('hidden');
					strength_message.addClass('hidden');
					$('.page-card-head .indicator')
						.removeClass().addClass('indicator green')
						.html(__('Password Updated'));
					if(r.message) {
						frappe.msgprint(__("Password Updated"));
	                    setTimeout(function() {
							window.location.href = r.message;
	                    }, 2000);
					}
				}
			}
		});

        return false;
	});

	window.strength_indicator = $('.password-strength-indicator');
	window.strength_message = $('.password-strength-message');

	$('#new_password').on('keyup', function() {
		window.clear_timeout();
		window.timout_password_strength = setTimeout(window.test_password_strength, 200);
	});

	window.test_password_strength = function() {
		window.timout_password_strength = null;

		var args = {
			new_password: $("#new_password").val()
		}

		if (!args.new_password) {
			set_strength_indicator('grey', {'warning': __('Please enter the password') });
			return;
		}

		return frappe.call({
			type: 'GET',
			method: 'frappe.core.doctype.user.user.test_password_strength',
			args: args,
			callback: function(r) {
				// console.log(r.message);
			},
			statusCode: {
				401: function() {
					$('.page-card-head .indicator').removeClass().addClass('indicator red')
						.text(__('Invalid Password'));
				},
				200: function(r) {
					if (r.message && r.message.entropy) {
						var score = r.message.score,
							feedback = r.message.feedback;

						feedback.crack_time_display = r.message.crack_time_display;
						feedback.score = score;

						if (score < 2) {
							set_strength_indicator('red', feedback);
						} else if (score < 4) {
							set_strength_indicator('yellow', feedback);
						} else {
							set_strength_indicator('green', feedback);
						}
					}
				}
			}

		});
	};

	window.set_strength_indicator = function(color, feedback) {
		var message = [];
		if (feedback) {
			if (feedback.suggestions && feedback.suggestions.length) {
				message = message.concat(feedback.suggestions);
			} else if (feedback.warning) {
				message.push(feedback.warning);
			}

			if (!message.length && feedback.crack_time_display) {
				message.push(__('This password will take {0} to crack', [feedback.crack_time_display]));
				if (feedback.score > 3) {
					message.push('👍');
				}
			}
		}

		strength_indicator.removeClass().addClass('password-strength-indicator indicator ' + color);
		strength_message.text(message.join(' ') || '').removeClass('hidden');
		// strength_indicator.attr('title', message.join(' ') || '');
	}

	window.clear_timeout = function() {
		if (window.timout_password_strength) {
			clearTimeout(window.timout_password_strength);
			window.timout_password_strength = null;
		}
	};
});