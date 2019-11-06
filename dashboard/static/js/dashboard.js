let delete_project_id = 0;
let last_scroll_y = null;

// UX
function hide_edit_controls() {
    hide_top_bar_controls();
    $(".top-button").show();
    $("#save-icon").hide();
}

var main = function() {
    hide_edit_controls();
};

$(document).ready(main);

