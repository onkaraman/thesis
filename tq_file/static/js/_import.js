var picked_upload_file = null;


function gen_uuid() {
    let uuid = ""
    for (var i = 0; i < 80; i++) {
        uuid += Math.floor(Math.random() * 16).toString(16);
    }
    return uuid
}

function request_file_parse(task_id) {
    start_loading_animation();
    $("#upload-button").prop("disabled", true);

    $.ajax({
        url: "/api/tq/upload?task_id=" + task_id,
        type: 'POST',
        data: new FormData($('#upload-form')[0]),
        cache: false,
        contentType: false,
        processData: false,

        success: function (data) {
            stop_loading_animation();
            var json = JSON.parse(data);

            if (json.success === true) {
                request_load_tqs();
                $("#upload-button").prop("disabled", false);
            } else {
            }
        },
        error: function (data, exception) {
            stop_loading_animation();
            alert(data.responseText);
        }
    });
}

var main = function () {
    let upload_button = $("#upload-button");

    $('input[type="file"]').change(function (e) {
        let file_name = e.target.files[0].name;
        picked_upload_file = e.target.files[0];

        $("#selected-file").text(file_name);
        upload_button.prop("disabled", false);
    });

    upload_button.click(function (e) {
        e.preventDefault();
        upload_button.prop("disabled", true);

        let task_id = gen_uuid();
        request_file_parse(task_id);
    });
};

$(document).ready(main);