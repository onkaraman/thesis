var file_name = "offline";

// Helpers
function apply_download_url() {
    let data = new Blob([ace.edit("export-editor").getValue()], {type: 'text/plain'});
    let download_file = window.URL.createObjectURL(data);

    let dl_link = $("#download-link");
    dl_link.prop("download", file_name + ".json");
    dl_link.prop("href", download_file);
}

// Requests
function request_get_ff() {
    start_loading_animation();

    $.ajax({
        url: "/api/ff/export_content",
        success: function (data) {
            stop_loading_animation();

            let json = JSON.parse(data);
            if (json.project_name) {
                file_name = json.fusion_name;
                config_editor();
                ace.edit("export-editor").setValue(JSON.stringify(json, null, '\t'));
                ace.edit("export-editor").clearSelection();

                apply_download_url();
                $("#export-editor").show();
                $("#download-link").css("display", "block");

                $("#export-container").show();
                $("#loading-content-container").hide();
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

    editor.getSession().on('change', function () {
        apply_download_url()
    });
}

var main = function () {
    $("#export-editor").hide();
    request_get_ff();
};

$(document).ready(main);