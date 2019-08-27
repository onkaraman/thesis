function request_tq_table_data(id) {
    start_loading_animation();

    $.ajax({
        data: {"id": id},
        url: "/api/tq/view",
        success: function (data) {
            stop_loading_animation();
            let json = JSON.parse(data);

            if (json.success) {
                console.log(json.table_data);
                render_table_heads(json.table_data["cols"]);
                render_table_body(json.table_data["cols"], json.table_data["rows"]);
            }
        },
        error: function (data, exception) {
            alert(data.responseText);
        }
    });
}

function render_table_heads(cols) {
    let head_tr = $("#head-tr");
    head_tr.empty();

    cols.forEach(function (i) {
        head_tr.append('<th scope="col">' + i + '</th>');
    });
}

function render_table_body(cols, rows) {
    let table_body = $("#table-body");
    table_body.empty();

    let index = 1;
    rows.forEach(function (row) {
        let to_append = '<tr>';

        let i;
        for (i = 0; i < cols.length; i += 1) {
            if (cols[i] === "#") {
                to_append += '<td>' + index + '</td>';
                index += 1;
            }
            else {
                to_append += '<td>' + row[cols[i]] + '</td>';
            }
        }

        to_append += '</tr>';
        table_body.append(to_append);
    });
}

var main = function () {
    let id = $("#tq-id").attr("pk");
    request_tq_table_data(id);
};

$(document).ready(main);