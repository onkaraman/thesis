var anim_loop = false;
let next_anim_color = "#00aad2";
let next_anim = true;


jQuery.extend({
    //https://stackoverflow.com/questions/690781/debugging-scripts-added-via-jquery-getscript-function
    getScript: function (url, callback) {
        var head = document.getElementsByTagName("head")[0];
        var script = document.createElement("script");
        script.src = url;

        // Handle Script loading
        {
            var done = false;

            // Attach handlers for all browsers
            script.onload = script.onreadystatechange = function () {
                if (!done && (!this.readyState ||
                    this.readyState == "loaded" || this.readyState == "complete")) {
                    done = true;
                    if (callback)
                        callback();

                    // Handle memory leak in IE
                    script.onload = script.onreadystatechange = null;
                }
            };
        }

        head.appendChild(script);

        // We handle everything using the script element injection
        return undefined;
    },
});

function getQueryParams(qs) {
    qs = qs.split("+").join(" ");
    var params = {},
        tokens,
        re = /[?&]?([^=]+)=([^&]*)/g;

    while (tokens = re.exec(qs)) {
        params[decodeURIComponent(tokens[1])]
            = decodeURIComponent(tokens[2]);
    }
    return params;
}

let $_GET = getQueryParams(document.location.search);

function is_valid_email(emailAddress) {
    var pattern = new RegExp(/^(("[\w-+\s]+")|([\w-+]+(?:\.[\w-+]+)*)|("[\w-+\s]+")([\w-+]+(?:\.[\w-+]+)*))(@((?:[\w-+]+\.)*\w[\w-+]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$)|(@\[?((25[0-5]\.|2[0-4][\d]\.|1[\d]{2}\.|[\d]{1,2}\.))((25[0-5]|2[0-4][\d]|1[\d]{2}|[\d]{1,2})\.){2}(25[0-5]|2[0-4][\d]|1[\d]{2}|[\d]{1,2})\]?$)/i);
    return pattern.test(emailAddress);
}

function hide_controls() {
    $("#left-panel").hide();
    $("#right-panel").hide();
    $("#project-name").hide();
    $(".top-button").hide();
    $("#left-panel-hamburger").css("opacity", "0");
}


function left_panel_toggle() {
    if ($("#left-panel").width() > 100) {
        $("#left-panel").css("width", "56px");
        $(".panel-button p").hide();
        $(".panel-header").hide();
    } else if ($("#left-panel").width() < 100) {
        $("#left-panel").css("width", "220px");
        $(".panel-button p").show();
        $(".panel-header").show();
    }
}

function animate_loading() {
    $("#top-bar").animate({
        outlineColor: next_anim_color
    }, 600, function () {
        if (!next_anim) {
            next_anim_color = "#5097ab";
            next_anim = true;
        } else {
            next_anim_color = "#d6d6d6";
            next_anim = false;
        }
        if (anim_loop) animate_loading();
        else $("#top-bar").css("outline-color", "#d6d6d6");
    });
}

function start_loading_animation() {
    $("#top-bar").animate({
        "outline-width": "2px"
    }, 300, function () {
        anim_loop = true;
        animate_loading();
    });
}

function stop_loading_animation() {
    $("#top-bar").animate({
        "outline-width": "1px"
    }, 300, function () {
        anim_loop = false;
    });
}

function request_template_include(url, data_dict) {
    start_loading_animation();

    $.ajax({
        url: url,
        data: data_dict,
        success: function (data) {
            stop_loading_animation();
            let json = JSON.parse(data);
            let html = json.html.replace(new RegExp("\>[\s]+\<", "g"), "><");

            // Apply css
            $("head link#dynamic-css").attr("href", json.css);
            // Apply js
            $.getScript(json.js, function () {
                console.log("Included " + json.js);
            });

            $("#center-panel").html(html);
        },
        error: function (data, exception) {
            alert(data.responseText);
        }
    });
}

var main = function () {
    $("#left-panel-hamburger").click(function (e) {
        left_panel_toggle();
    });

};


$(document).ready(main);