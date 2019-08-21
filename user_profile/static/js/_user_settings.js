function request_logout() {
    start_loading_animation();

    $.ajax({
        url: "/api/user/logout",
        success: function (data) {
            stop_loading_animation();

            let json = JSON.parse(data);
            if (json.success) {
                window.location = "/login";
            }
        },
        error: function (data, exception) {
            stop_loading_animation();
            alert(data.responseText);
        }
    });
}

var main = function() {
    $("#logout-button").click(function (e) {
        request_logout();
    });
};

$(document).ready(main);