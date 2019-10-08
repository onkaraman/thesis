function config_editor() {
    ace.edit("export-editor", {
        mode: "ace/mode/json",
        theme: "ace/theme/dawn",
        selectionStyle: "text",
    });

    let editor = ace.edit("editor");
    editor.renderer.setScrollMargin(10, 10);
}

var main = function() {
    config_editor();
};

$(document).ready(main);