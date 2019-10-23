// Requests
function request_project_details() {
    start_loading_animation();

    $.ajax({
        url: "/api/project/details",
        data: {},
        success: function (data) {
            stop_loading_animation();

            let json = JSON.parse(data);
            if (json.success) {
                $("#creation-p #creation-date").text(json.creation_date);
                $("#creation-p #days").text(json.days_past);
                $("#creation-p").css("display", "block");
            }
        },
        error: function (data, exception) {
            alert(data.responseText);
        }
    });
}

function request_create_note() {
    start_loading_animation();

    let name = $("#create-note-container #name");
    let content = $("#create-note-container #content");
    let upload_button = $("#create-note-container #upload-button");

    upload_button.prop("disabled", true);

    $.ajax({
        url: "/api/note/create",
        data: {
            "name": name.val(),
            "content": content.val()
        },
        success: function (data) {
            upload_button.prop("disabled", false);
            stop_loading_animation();

            let json = JSON.parse(data);
            if (json.success) {
                name.val("");
                content.val("");
                request_all_notes();
            }
        },
        error: function (data, exception) {
            upload_button.prop("disabled", false);
            alert(data.responseText);
        }
    });
}

function request_delete_note(id) {
    start_loading_animation();

    $.ajax({
        url: "/api/note/delete",
        data: {"id": id},
        success: function (data) {
            stop_loading_animation();

            let json = JSON.parse(data);
            if (json.success) request_all_notes();
        },
        error: function (data, exception) {
            alert(data.responseText);
        }
    });
}

function request_all_notes() {
    start_loading_animation();

    $.ajax({
        url: "/api/note/all",
        data: {},
        success: function (data) {
            stop_loading_animation();

            let json = JSON.parse(data);

            $("#notes-box").empty();
            json.items.forEach(function (i) {
                add_note_item(i);
            });
        },
        error: function (data, exception) {
            upload_button.prop("disabled", false);
            alert(data.responseText);
        }
    });
}

// UX
function add_note_item(i) {
    $("#notes-box").append('' +
        '<div class="note-item" id="'+ i.id + '">' +
            '<i class="far fa-times-circle close"></i>' +
            '<p class="note-name"><i class="far fa-lightbulb"></i>' + i.name + '</p>'+
            '<p class="note-content">' + i.content + '</p>' +
        '</div>');
}

function register_notes_events() {
    let name = $("#create-note-container #name");
    let content = $("#create-note-container #content");
    let upload_button = $("#create-note-container #upload-button");

    content.keyup(function (e) {
        upload_button.prop("disabled", !(name.val().length >= 3 && content.val().length >= 3));
    });

    upload_button.click(function (e) {
        request_create_note();
    });
}

var main = function () {
    $("#creation-p").hide();
    request_project_details();
    request_all_notes();
    register_notes_events();

    setTimeout(function () {
        $("#auto-save").fadeOut();
    }, 5000)
};

$(document).ready(main);

$(document).on("click", ".note-item .close", function (e) {
    e.preventDefault();
    let id = $(this).parent().attr("id");
    request_delete_note(id);

});

//# sourceURL=/static/js/_new_project.js