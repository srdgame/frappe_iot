frappe.ready(function() {
	$(".form-enable-iot").submit(function() {
		alert("AAAAAAAAAAAAAAAAAAAA");
  		$(this).ajaxSubmit({
			success: function (responseText, statusText, xhr, $form) {
				alert(responseText);
			}
		});
		return false;
	});
});