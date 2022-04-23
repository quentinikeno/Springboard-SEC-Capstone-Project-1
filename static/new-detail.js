$(window).on("load", () => {
	$(".spinner-loading-div").fadeOut(400, function () {
		$(this).remove();
		$(".worksheet-preview").fadeIn(400, () => {
			$(".worksheet-preview a").removeClass("d-none");
		});
	});
});

// On submit, disable the form submission button and show a loading spinner.
$(".upload-form").on("submit", function () {
	buttonLoading = $(
		'<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>'
	);
	submitButton = $(".upload-form button");
	submitButton
		.text("Loading...  ")
		.append(buttonLoading)
		.prop("disabled", true);
});
