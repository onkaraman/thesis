/*!
 * Daimler Main JS
 */

$(document).ready(function() {

	// init lightbox plugin
	function initLightbox() {

		// provider/privacy layer
		$(".privacy-disclaimer").off().on('click', function (event) {
			event.preventDefault();
			$.fancybox({
				type: 'inline',
				arrows: false,
				closeBtn: true,
				content: $('#privacyPolicy'),
				padding: '0',
				wrapCSS: 'info-layer',
				autoCenter: true,
				autoResize: true,
				scrolling: 'auto',
				beforeShow: function () {
					//
				},
				afterShow: function () {
					//
				},
				onUpdate: function () {
					//
				},
				helpers: {
					overlay: {
						locked: true
					}
				}
			});
		});
	}


	initLightbox();
});
