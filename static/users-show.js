// On submit, disable the form submission button and show a loading spinner.
$("form.delete-form").on("submit", function () {
	buttonLoading = $(
		'<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>'
	);
	submitButton = $("button", this);
	submitButton
		.text("Deleting...  ")
		.append(buttonLoading)
		.prop("disabled", true);
});
