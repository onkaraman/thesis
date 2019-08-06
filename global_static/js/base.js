var is_mobile = false;
var anim_loop = true;
var next_anim = false;
var next_anim_color = "#9e9e9e";

function resize_elements() {
    $("#top-mid").css("width", $("#top-content").width()
        - $("#top-left").outerWidth()
        - $("#top-right").outerWidth());
}

function adapt_mobile() {
    if ($(window).outerWidth() <= 1500 || /iPhone|iPad|iPod|Android/i.test(navigator.userAgent)) is_mobile = true;
    else is_mobile = false;

    replace_css();
    return is_mobile;
}

function animate_hint_color(selector) {
     $(".loading-hint").animate({
         backgroundColor: next_anim_color
     }, 500, function () {
         if (!next_anim) {
             next_anim_color = "#b7b7b7";
             next_anim = true;
         } else {
             next_anim_color = "#a0a0a0";
             next_anim = false;
         }
         if (anim_loop)  animate_hint_color();
     });
}

function start_loading_animation(selector=".loading-hint") {
    anim_loop = true;
    animate_hint_color(selector);
}

function stop_loading_animation() {
    anim_loop = false;
    next_anim_color = "#9e9e9e";
}


var main = function () {
    //is_mobile = adapt_mobile();
    resize_elements();

    $(window).resize(function () {
        //adapt_mobile();
        resize_elements();
    });

    $('#logo-container, #nav-dashboard').click(function (e) {
        window.location = "/";
    });

    $("#nav-management").click(function (e){
        window.location = "/management";
    });

    $("#account-settings").click(function (e) {
        window.location = "/settings";
    });
};


$(document).ready(main);