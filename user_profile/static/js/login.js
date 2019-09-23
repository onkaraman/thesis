function request_login() {
    start_loading_animation();

    $.ajax({
        type: 'POST',
        headers:{
            "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val()
        },
        url: "/api/user/login/",
        data: {
            "email": $("#corp-mail").val(),
            "pw": $("#password").val()
        },
        success: function (data) {
            stop_loading_animation();

            var json = JSON.parse(data);

            if (json.success) {
                window.location = "/";
            } else {
                let error = $("#server-response");
                error.show();
                error.text(json.msg);
            }
        },
        error: function (data, exception) {
            alert(data.responseText);
        }
    });
}

function validate() {
    let email = $("#corp-mail");
    let pw = $("#password");

    let error = $("#server-response");
    error.hide();

    if (!email.val().trim().endsWith("@daimler.com")) {
        error.show();
        error.text("Die E-Mail Adresse scheint nicht von Daimler zu sein.");
    } else if (pw.val().length < 8) {
        error.show();
        error.text("Das eingebene Passwort ist zu kurz.");
    } else {
        return true;
    }
    return false;
}

var main = function () {
    hide_top_bar_controls();

    $("#login-button").click(function (e) {
        if (validate()) request_login();
    });
};

$(document).ready(main);
