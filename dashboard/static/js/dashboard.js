let delete_project_id = 0;
let last_scroll_y = null;

// UX
function hide_edit_controls() {
    hide_top_bar_controls();
    $(".top-button").show();
    $("#save-icon").hide();
}

function show_simple_modal(title, msg, yes_callback) {
    $("#simple-modal #title").text(title);
    $("#simple-modal #msg").html(msg);

    last_scroll_y = $(window).scrollTop();

    let simple_modal = $("#simple-modal");
    let spanner = $("#spanner");

    $(simple_modal[0].getElementsByClassName("modal-yes-button")).click(function (e) {
        yes_callback();
    });

    $("html, body").animate({ scrollTop: 0 }, "slow");

    spanner.fadeIn(200);
    simple_modal.fadeIn(200);
}

function hide_simple_modal() {
    $("#simple-modal").fadeOut(100);
    $("#spanner").fadeOut(100);
    $("html, body").animate({ scrollTop: last_scroll_y }, "slow");
}

function add_tq_ui(item) {
    $("#tqs-container").append(
        '<div class="panel-button accented tq-item" id="' + item.id + '">' +
            '<i class="far fa-clone panel-icon"></i>' +
            '<p>' + item.name + '</p>' +
        '</div>'
    );
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
};

$(document).ready(main);

