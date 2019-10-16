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
    })) ;

};

$(document).ready(main);

