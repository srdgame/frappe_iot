frappe.ready(function() {

	$('.user-enabled-switch').on('click', function() {
		var $btn = $(this);
		if($btn.attr('data-enabled')==='True') {
			reload_items('True', 'user', $btn);
		} else {
			reload_items('False', 'user', $btn);
		}
	})

	var start = 10;
	$(".more-users").click(function() {
		more_items('user', true);
	});


	var reload_items = function(enabled, item, $btn) {
		$.ajax({
			method: "GET",
			url: "/",
			dataType: "json",
			data: {
				cmd: "iot.templates.pages.iot_enterprises.get_"+ item +"_html",
				enterprise: '{{ doc.name }}',
				enabled: enabled,
			},
			dataType: "json",
			success: function(data) {
				if(typeof data.message == 'undefined') {
					$('.enterprise-'+ item).html("No "+ enabled +" "+ item);
					$(".more-"+ item).toggle(false);
				}
				$('.enterprise-'+ item).html(data.message);
				$(".more-"+ item).toggle(true);

				// update status
				if(enabled==='True') {
					$btn.html(__('Show closed')).attr('data-status', 'Open');
				} else {
					$btn.html(__('Show open')).attr('data-status', 'Closed');
				}
			}
		});

	}

	var more_items = function(item, enabled){
		if(enabled)
		{
			var enabled = $('.enterprise-'+ item +'-section .btn-group .bold').hasClass('btn-closed-'+ item)
				? 'closed' : 'True';
		}
		$.ajax({
			method: "GET",
			url: "/",
			dataType: "json",
			data: {
				cmd: "iot.templates.pages.iot_enterprises.get_"+ item +"_html",
				enterprise: '{{ doc.name }}',
				start: start,
				enabled: enabled,
			},
			dataType: "json",
			success: function(data) {

				$(data.message).appendTo('.enterprise-'+ item);
				if(typeof data.message == 'undefined') {
					$(".more-"+ item).toggle(false);
				}
			start = start+10;
			}
		});
	}

	var close_item = function(item, item_name){
		var args = {
			enterprise: '{{ doc.name }}',
			item_name: item_name,
		}
		frappe.call({
			btn: this,
			type: "POST",
			method: "iot.templates.pages.iot_enterprises.set_"+ item +"_status",
			args: args,
			callback: function(r) {
				if(r.exc) {
					if(r._server_messages)
						frappe.msgprint(r._server_messages);
				} else {
					$(this).remove();
				}
			}
		})
		return false;
	}
});