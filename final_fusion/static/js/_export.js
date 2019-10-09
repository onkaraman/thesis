function request_get_ff() {
    start_loading_animation();

    $.ajax({
        url: "/api/ff/export_content",
        success: function (data) {
            stop_loading_animation();

            let json = JSON.parse(data);
            if (json.project_name) {
                config_editor();
                ace.edit("export-editor").setValue(JSON.stringify(json, null, '\t'));
                $("#export-editor").show();
            }
        },
        error: function (data, exception) {
            alert(data.responseText);
        }
    });
}

function config_editor() {
    ace.edit("export-editor", {
        mode: "ace/mode/json",
        theme: "ace/theme/dawn",
        selectionStyle: "text",
    });

    let editor = ace.edit("export-editor");
    editor.renderer.setScrollMargin(5, 5);
}

var main = function() {
    $("#export-editor").hide();
    request_get_ff();
};

$(document).ready(main);