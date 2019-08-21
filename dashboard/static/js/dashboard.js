function hide_edit_controls() {
    hide_controls();
    $("#project-name").hide();
    $(".top-button").show();
    $("#save-icon").hide();
}

function register_events() {
    $("#user-icon").click(function (e) {
        request_template_include("/include/user/settings", {});
    });

    $("#load-project").click(function (e) {
        request_template_include("/include/project/user_projects", {})
    });
}

var main = function() {
    hide_edit_controls();
    register_events();
};

$(document).ready(main);