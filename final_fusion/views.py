import json
from django.http import HttpResponse
from security.args_checker import ArgsChecker
import security.token_checker as token_checker
from tq_file.models import TQFile
from final_fusion_column.models import FinalFusionColumn
from final_fusion.models import FinalFusion
from project.models import Project
from rule_module.rule_queue import RuleQueue
import dashboard.includer as dashboard_includer


def do_select_column(request):
    """
    do_select_column
    """
    added = False

    valid_user = token_checker.token_is_valid(request)
    if valid_user and "tq_id" in request.GET and ArgsChecker.is_number(request.GET["tq_id"]) \
            and "col_name" in request.GET and not ArgsChecker.str_is_malicious(request.GET["col_name"]):
        tq_id = request.GET["tq_id"]
        col_name = request.GET["col_name"]

        tq = TQFile.objects.get(pk=tq_id)
        col = tq.get_column(col_name)

        ef = FinalFusion.objects.get(project=Project.objects.get(pk=valid_user.last_opened_project_id))
        ffc_fetch = FinalFusionColumn.objects.filter(final_fusion=ef, source_tq=tq, source_column_name=col_name)

        if len(ffc_fetch) == 0:
            ffc = FinalFusionColumn.objects.create(
                final_fusion=ef,
                source_tq=tq,
                source_column_name=col_name,
                display_column_name=col_name,
                rows_json=json.dumps(col)
            )
            added = True
        elif len(ffc_fetch) == 1:
            if not ffc_fetch[0].archived:
                ffc_fetch[0].archived = True
                ffc_fetch[0].save()
                added = False
            else:
                ffc_fetch[0].archived = False
                ffc_fetch[0].save()
                added = True

    return HttpResponse(json.dumps({"added": added}))


def do_rename(request):
    """
    do_rename
    """
    success = False
    valid_user = token_checker.token_is_valid(request)

    if valid_user and "name" in request.GET and not ArgsChecker.str_is_malicious(request.GET["name"]):
        proj = Project.objects.get(pk=valid_user.last_opened_project_id)
        ff = FinalFusion.objects.get(project=proj)
        ff.name = request.GET["name"]
        ff.save()
        success = True

    return HttpResponse(json.dumps({"success": success}))


def do_get_col_vars(request):
    """
    do_get_col_vars
    """
    success = False
    cv = {}
    valid_user = token_checker.token_is_valid(request)

    if valid_user:
        proj = Project.objects.get(pk=valid_user.last_opened_project_id)
        ff = FinalFusion.objects.get(project=proj)
        cv = ff.get_col_vars()
        success = True

    return HttpResponse(json.dumps({
        "success": success,
        "cv": cv
    }))


def i_render_preview_tf(request):
    """
    i_render_preview_tf
    """
    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        proj = Project.objects.get(pk=valid_user.last_opened_project_id)
        ff = FinalFusion.objects.get(project=proj)

        dic = {
            "name": ff.name
        }
        return dashboard_includer.get_as_json("final_fusion/_preview.html")


def get_preview_table(user_profile):
    """
    get_preview_table
    """
    out_headers = []
    out_rows = []

    proj = Project.objects.get(pk=user_profile.last_opened_project_id)
    ff = FinalFusion.objects.get(project=proj)
    ffc_cols = FinalFusionColumn.objects.filter(final_fusion=ff, archived=False).order_by("pk")

    header_rows = []
    deepest_col = 0

    for ffc_col in ffc_cols:
        if ffc_col.rm_dependency and \
                ffc_col.source_column_name not in ffc_col.rm_dependency.depending_dynamic_columns():
            ffc_col.delete()
        else:
            as_json = ffc_col.get_as_json()

            out_headers.append({"name": as_json["name"], "id": ffc_col.pk })
            ffc_rows = json.loads(as_json["rows"])

            header_rows.append({
                "name": as_json["name"],
                "id": ffc_col.pk,
                "rows": ffc_rows
            })

            if len(ffc_rows) > deepest_col:
                deepest_col = len(ffc_rows)

    try:
        for i in range(deepest_col):
            row = {}
            for h in header_rows:
                value = "-"

                if len(h["rows"]) > i:
                    value = h["rows"][i]
                row[h["name"]] = value
            out_rows.append(row)
    except IndexError:
        pass

    return {
        "out_headers": out_headers,
        "out_rows": out_rows
    }


def render_preview_table(request):
    """
    render_preview_table
    """
    success = False
    table = {"out_headers": None, "out_rows": None}

    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        table = get_preview_table(valid_user)

        if len(table["out_rows"]) > 0:
            success = True

    return HttpResponse(json.dumps(
        {
            "success": success,
            "headers": table["out_headers"],
            "rows": table["out_rows"]
        }))


def render_preview_table_with_rm(request):
    """
    render_preview_table_with_rm
    """
    success = False
    table = {"out_headers": None, "out_rows": None}

    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        table = get_preview_table(valid_user)
        rq = RuleQueue(table)
        rq.add_all_user_rule_modules(valid_user)
        rq.apply()
        table["out_rows"] = rq.table["out_rows"]

        if len(table["out_rows"]) > 0:
            success = True

    return HttpResponse(json.dumps(
        {
            "success": success,
            "headers": table["out_headers"],
            "rows": table["out_rows"]
        }))
