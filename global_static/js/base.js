var anim_loop = false;
let next_anim_color = "#00aad2";
let next_anim = true;


// jQuery
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
                    if (callback) callback();
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

// Helpers
function is_valid_email(emailAddress) {
    var pattern = new RegExp(/^(("[\w-+\s]+")|([\w-+]+(?:\.[\w-+]+)*)|("[\w-+\s]+")([\w-+]+(?:\.[\w-+]+)*))(@((?:[\w-+]+\.)*\w[\w-+]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$)|(@\[?((25[0-5]\.|2[0-4][\d]\.|1[\d]{2}\.|[\d]{1,2}\.))((25[0-5]|2[0-4][\d]|1[\d]{2}|[\d]{1,2})\.){2}(25[0-5]|2[0-4][\d]|1[\d]{2}|[\d]{1,2})\]?$)/i);
    return pattern.test(emailAddress);
}

function unbind_methods_with_namespace(ns) {
    let events = $._data( $(document)[0], "events" );
    for (let property in events) {
        for (let item in events[property]) {

            let handler = events[property][item];
            if (handler.namespace === ns) {
                $(document).off(property + "." + ns);
                console.log("Unbound: " + handler.type + "." + handler.namespace);
            }
        }
    }
}

// Requests
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

            try {
                // Apply js
                unbind_methods_with_namespace(json.namespace);

                $.getScript(json.js, function () {
                    console.log("Included " + json.js);
                });

            } catch (error) {
            }

            $("#center-panel").empty();
            $("#center-panel").html(html);
        },
        error: function (data, exception) {
            alert(data.responseText);
        }
    });
}

function request_start_new_project() {
    start_loading_animation();
    $.ajax({
        url: "/api/project/new",
        success: function (data) {
            stop_loading_animation();
            let json = JSON.parse(data);

            if (json.success) {
                $("#project-name p").text(json.name);
                show_new_project_ui();
            }

            request_template_include("/include/project/new");
        },
        error: function (data, exception) {
            alert(data.responseText);
        }
    });
}

function request_rename_project(new_name) {
    let name_rename = $("#project-rename");
    let project_name_p = $("#project-name p");

    start_loading_animation();
    $.ajax({
        url: "/api/project/rename",
        data: {
            "name": new_name
        },
        success: function (data) {
            stop_loading_animation();
            let json = JSON.parse(data);

            if (json.success) {
                project_name_p.text(new_name);
                project_name_p.show();
                name_rename.hide();
            }
        },
        error: function (data, exception) {
            stop_loading_animation();
            alert(data.responseText);
        }
    });
}

// UX
function hide_top_bar_controls() {
    $("#left-panel").hide();
    $("#right-panel").hide();
    $("#project-name").hide();
    $(".top-button").hide();
    $("#left-panel-hamburger").css("opacity", "0");
}

function fit_simple_modal() {
    let simple_modal = $("#simple-modal");
    simple_modal.css("margin-left", ($(document).width() / 2) - simple_modal.outerWidth() / 2);
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

function show_new_project_ui() {
    $("#left-panel").show("slide", {direction: "left"}, 300);
    $("#project-name").show();
    $("#left-panel-hamburger").css("opacity", "1");
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

function reset_left_panel() {
    $("#tqs-container").empty();
    //$("#rms-container").empty();
    $("#endfusion-button").hide();
}

function start_new_project() {
    request_start_new_project();
}


var main = function () {
    fit_simple_modal();
    $(window).resize(function () {
        fit_simple_modal();
    });
    reset_left_panel();

    let project_rename = $("#project-rename");
    let project_name_p = $("#project-name p");

    $("#logo").click(function (e) {
        window.location = "/";
    });

    $("#left-panel-hamburger").click(function (e) {
        left_panel_toggle();
    });

    $("#new-project").click(function (e) {
        start_new_project();
    });

    $("#project-name").click(function (e) {
        project_name_p.hide();
        project_rename.val(project_name_p.text());
        project_rename.show();
        project_rename.focus();
    });

    project_rename.keyup(function (e) {
        if (e.key === "Escape") {
            project_rename.hide();
            project_name_p.show();
        } else if (e.key === "Enter") {
            request_rename_project(project_rename.val());
        }
    });

    $("#user-icon").click(function (e) {
        hide_edit_controls();
        request_template_include("/include/user/settings", {});
    });

    $("#load-project").click(function (e) {
        hide_edit_controls();
        request_template_include("/include/project/user_projects", {})
    });

    $("#add-tq").click(function (e) {
        request_template_include("/include/tq/import", {})
    });

    $("#rms-container").click(function (e) {
        request_template_include("/include/tf/preview", {})
    });

};


$(document).ready(main);