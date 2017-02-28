frappe.ready(function() {
	$(".form-enable-iot").submit(function() {
  		$(this).ajaxSubmit({
			success: function (responseText, statusText, xhr, $form) {
				alert(responseText);
			}
		})
	});
});