frappe.ready(function() {
	alert($(".form-enable-iot"));
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