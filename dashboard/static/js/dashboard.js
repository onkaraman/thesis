let delete_project_id = 0;

// UX
function hide_edit_controls() {
    hide_controls();
    $("#project-name").hide();
    $(".top-button").show();
    $("#save-icon").hide();
}

function show_simple_modal(title, msg) {
    $("#simple-modal #title").text(title);
    $("#simple-modal #msg").html(msg);

    let simple_modal = $("#simple-modal");
    let spanner = $("#spanner");

    spanner.fadeIn(200);
    simple_modal.fadeIn(200);
}

function hide_simple_modal() {
    $("#simple-modal").fadeOut(100);
    $("#spanner").fadeOut(100);
}

function register_events() {
    $("#user-icon").click(function (e) {
        hide_edit_controls();
        request_template_include("/include/user/settings", {});
    });

    $("#load-project").click(function (e) {
        hide_edit_controls();
        request_template_include("/include/project/user_projects", {})
    });
}

// Requests
function request_delete_project() {
    start_loading_animation();

    $.ajax({
        url: "/api/project/delete",
        data: {
            "id": delete_project_id,
        },
        success: function (data) {
            stop_loading_animation();
            delete_project_id = 0;

            let json = JSON.parse(data);

            if (json.success) {
                hide_simple_modal();
                $("#load-project").click();
            }
        },
        error: function (data, exception) {
            alert(data.responseText);
        }
    });
}

var main = function() {
    hide_edit_controls();
    register_events();
};

$(document).ready(main);

$(document).on("click", ".project-delete", function (e) {
    e.preventDefault();
    fit_simple_modal();

    delete_project_id = e.currentTarget.parentElement.getAttribute("id");
    let project_name = $(e.currentTarget.parentElement.getElementsByClassName("name")[0]).text();

    let msg = "Möchten Sie wirklich <b>" + project_name + "</b> löschen?";
    $("html, body").animate({ scrollTop: 80 }, "slow");
    show_simple_modal("Projekt löschen", msg);
});

$(document).on("click", "#simple-modal #yes", function (e) {
    e.preventDefault();
    request_delete_project();
});


$(document).on("click", "#simple-modal #no", function (e) {
    e.preventDefault();
    hide_simple_modal();
});

$(document).on("click", "#simple-modal #close", function (e) {
    e.preventDefault();
    hide_simple_modal();
});
