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

var main = function () {
    request_load_tqs();

    let click_area = $(".project-item .click-area");

    if (click_area.mouseover(function (e) {
        let subject = $(e.currentTarget.parentElement);
        subject.css("background-color", "#d0d0d0");
        subject.css("border-bottom-color", "#0096b3");
    })) ;

    if (click_area.mouseleave(function (e) {
        let prev_background_color = "#e6e6e6";
        let prev_border_bottom_color = "#00677F";

        let subject = $(e.currentTarget.parentElement);
        subject.css("background-color", prev_background_color);
        subject.css("border-bottom-color", prev_border_bottom_color);
    })) ;

    if (click_area.click(function (e) {
        let id = $(e.currentTarget.parentElement).attr("id");
        request_load_project(id);
    }));

};

$(document).ready(main);

$(document).on("click", ".project-delete", function (e) {
    e.preventDefault();
    fit_modals();

    delete_project_id = e.currentTarget.parentElement.getAttribute("id");
    let project_name = $(e.currentTarget.parentElement.getElementsByClassName("name")[0]).text();

    let msg = "Möchten Sie wirklich <b>" + project_name + "</b> löschen?";
    show_simple_modal("Projekt löschen", msg, request_delete_project);
});