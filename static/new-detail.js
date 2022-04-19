$(window).on("load", () => {
	$(".spinner-loading-div").fadeOut(400, function () {
		$(this).remove();
		$(".worksheet-preview").fadeIn(400, () => {
			$(".worksheet-preview a").removeClass("d-none");
		});
	});
});
