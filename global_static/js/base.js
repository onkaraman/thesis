function left_panel_toggle() {
    if ($("#left-panel").width() > 100) {
        $("#left-panel").css("width", "56px");
        $(".panel-button p").hide();
        $(".panel-header").hide();
    } else if ($("#left-panel").width() < 100) {
        $("#left-panel").css("width", "220px");
        $(".panel-button p").show();
        $(".panel-header").show();
    }
}


let main = function () {
    $("#left-panel-hamburger").click(function (e) {
        left_panel_toggle();
    });

};


$(document).ready(main);