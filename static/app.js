const range_input = $("#number_questions");

function updateRangeVal() {
	$("#range-val").text(range_input.val());
}

$(document).ready(function () {
	updateRangeVal();
	range_input.on("change", updateRangeVal);
});
