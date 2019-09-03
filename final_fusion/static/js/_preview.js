// Requests
function request_tf_preview() {
    start_loading_animation();
    $.ajax({
        url: "/api/tf/preview_table",
        data: {

        },
        success: function (data) {
            stop_loading_animation();
            let json = JSON.parse(data);
        },
        error: function (data, exception) {
            stop_loading_animation();
            alert(data.responseText);
        }
    });
}

var main = function () {
    request_tf_preview();
};

$(document).ready(main);