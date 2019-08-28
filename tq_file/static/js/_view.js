var tq_table_cols = null;
var tq_table_rows = null;
var current_page = 1;
var all_pages = null;
var items_per_page = 10;

function request_tq_table_data(id) {
    start_loading_animation();

    $.ajax({
        data: {"id": id},
        url: "/api/tq/view",
        success: function (data) {
            stop_loading_animation();
            let json = JSON.parse(data);

            if (json.success) {
                render_table_heads(json.table_data["cols"]);
                render_table_body(json.table_data["cols"], json.table_data["rows"]);
            }
        },
        error: function (data, exception) {
            alert(data.responseText);
        }
    });
}

function request_rename_tq(new_name) {
    let name_display = $("#name-display");
    let tq_rename = $("#tq-rename");

    start_loading_animation();
    $.ajax({
        url: "/api/tq/rename",
        data: {
            "id": $("#tq-id").attr("pk"),
            "name": new_name
        },
        success: function (data) {
            stop_loading_animation();
            let json = JSON.parse(data);

            if (json.success) {
                $("#name-display h1").text(new_name);
                name_display.show();
                tq_rename.hide();
                request_load_tqs();
            }
        },
        error: function (data, exception) {
            stop_loading_animation();
            alert(data.responseText);
        }
    });
}

function request_delete_tq() {
    start_loading_animation();

    $.ajax({
        url: "/api/tq/delete",
        data: {
            "id": $("#tq-id").attr("pk")
        },
        success: function (data) {
            stop_loading_animation();

            let json = JSON.parse(data);
            if (json.success) {
                hide_simple_modal();
                request_load_tqs();
            }
        },
        error: function (data, exception) {
            alert(data.responseText);
        }
    });
}

// UX
function render_table_heads(cols) {
    let head_tr = $("#head-tr");
    head_tr.empty();

    cols.forEach(function (i) {
        head_tr.append('<th scope="col">' + i + '</th>');
    });
}

function render_table_body(cols, rows) {
    tq_table_rows = rows;
    tq_table_cols = cols;
    update_pagination();
}

function update_pagination() {
    $("#table-body").empty();

    let page_l = $("#page-l");
    let page_r = $("#page-r");

    all_pages = tq_table_rows.length/items_per_page;
    let offset = (current_page - 1) * items_per_page;
    if (current_page === 1) offset = 0;

    for (let i in tq_table_rows.slice(offset)) {
        i = parseInt(i, 10);
        if (i >= items_per_page) break;

        add_to_table(tq_table_cols, tq_table_rows.slice(offset)[i], (i + offset + 1));
    }

    $("#current-page").text(current_page + "/" + all_pages);

    page_l.attr("disabled", false);
    page_r.attr("disabled", false);

    if (current_page >= all_pages) page_r.attr("disabled", true);
    if (current_page === 1) page_l.attr("disabled", true);
}

function add_to_table(cols, row, index) {
    let to_append = '<tr>';

    let i;
    for (i = 0; i < cols.length; i += 1) {
        if (cols[i] === "#") {
            to_append += '<td>' + index + '</td>';
        } else {
            to_append += '<td>' + row[cols[i]] + '</td>';
        }
    }

    to_append += '</tr>';
    $("#table-body").append(to_append);
}

function register_events() {
    let name_container = $("#name-container");
    let name_display = $("#name-display");
    let tq_rename = $("#tq-rename");

    if (name_container.click(function (e) {
        name_display.hide();
        tq_rename.val($("#name-display h1").text());
        tq_rename.show();
        tq_rename.focus();
    })) ;

    tq_rename.keyup(function (e) {
        if (e.key === "Escape") {
            tq_rename.hide();
            name_display.show();
        } else if (e.key === "Enter") {
            request_rename_tq(tq_rename.val());
        }
    });

    $("#page-r").click(function (e) {
        e.preventDefault();

        if (current_page < all_pages) {
            current_page += 1;
            update_pagination();
        }
    });

    $("#page-l").click(function (e) {
        e.preventDefault();

        if (current_page >= 2) {
            current_page -= 1;
            update_pagination();
        }
    });

    $("#remove-tq-button").click(function (e) {
        show_simple_modal("Teilquelle löschen",
            "Möchten Sie wirklich diese TQ löschen?", request_delete_tq);
    });

}

var main = function () {
    let id = $("#tq-id").attr("pk");
    request_tq_table_data(id);
    register_events();
};

$(document).ready(main);
