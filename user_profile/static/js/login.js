function request_login() {
    $("#spinner").show();

    $.ajax({
        url: "/user/set_login",
        data: {
            "email": $("#corp-mail").val(),
            "pw": $("#password").val()
        },
        success: function (data) {
            $("#spinner").hide();

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
    let pw1 = $("#password");

    let error = $("#server-response");
    error.hide();

    if (!email.val().includes("@daimler.com")) {
        error.show();
        error.text("Die E-Mail Adresse scheint nicht von Daimler zu sein.");
    } else if (pw1.val().length < 8) {
        error.show();
        error.text("Das eingebene Passwort ist zu kurz.");
    } else {
        //request_login();
    }
}

var main = function () {
    hide_controls();

    $("#login-button").click(function (e) {
        validate();
    });
};

$(document).ready(main);
