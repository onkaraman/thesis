function hide_controls() {
    $("#left-panel").hide();
    $("#right-panel").hide();
    $("#project-name").hide();
    $(".top-button").hide();
    $("#left-panel-hamburger").css("opacity", "0");
}

function request_signup() {
    let error = $("#server-response");
    error.hide();
    start_loading_animation();

    $.ajax({
        url: "/api/user/set_signup",
        data: {
            "email": $("#corp-mail").val(),
            // TODO: Über POST
            "pw1": $("#password").val(),
            "pw2": $("#password-r").val()
        },
        success: function (data) {
            stop_loading_animation();

            let json = JSON.parse(data);

            if (json.success) {
                window.location = "/";
            } else {
                error.show();
                error.text("Server response: " + json.msg);
            }
        },
        error: function (data, exception) {
            alert(data.responseText);
        }
    });
}

function validate() {
    let error = $("#server-response");
    let email = $("#corp-mail").val();
    let pw1 = $("#password").val();
    let pw2 = $("#password-r").val();

    if (is_valid_email(email)) {
            if (pw1 === pw2 && pw1.length >= 8) {
                return true;
            }
            else {
                error.show();
                error.text("Passwords not equal");
            }
        } else {
            error.show();
            error.text("Email not valid");
        }
    return false;
}

var main = function () {
    hide_controls();

    $("#signup-button").click(function (e) {
        if (validate()) request_signup();
    });
};

$(document).ready(main);
