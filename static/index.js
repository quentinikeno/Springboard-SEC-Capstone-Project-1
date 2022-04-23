const range_input = $("#number_questions");

function updateRangeVal() {
	$("#range-val").text(range_input.val());
}

// Show value of range slider.
$(document).ready(function () {
	updateRangeVal();
	range_input.on("change", updateRangeVal);
});

// On submit, disable the form submission button and show a loading spinner.
$("#new-worksheet-form").on("submit", function () {
	buttonLoading = $(
		'<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>'
	);
	submitButton = $("#new-worksheet-form button");
	submitButton
		.text("Loading...  ")
		.append(buttonLoading)
		.prop("disabled", true);
});
