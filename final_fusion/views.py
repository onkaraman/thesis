import json
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
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


def do_append_cols(request):
    """
    do_append_cols
    """
    success = False
    valid_user = token_checker.token_is_valid(request)

    if valid_user and "a_id" in request.GET and ArgsChecker.is_number(request.GET["a_id"]) \
            and "b_id" in request.GET and ArgsChecker.is_number(request.GET["b_id"]) and \
            "remove_cols" in request.GET and not ArgsChecker.str_is_malicious(request.GET["remove_cols"]):

        try:
            a_col = FinalFusionColumn.objects.get(pk=request.GET["a_id"])
            b_col = FinalFusionColumn.objects.get(pk=request.GET["b_id"])

            appended_rows = json.loads(a_col.rows_json)

            for r in json.loads(b_col.rows_json):
                appended_rows.append(r)

            FinalFusionColumn.objects.create(
                final_fusion=a_col.final_fusion,
                source_column_name="%s~ + %s~" % (a_col.display_column_name[:2], b_col.display_column_name[:2]),
                display_column_name="%s~ + %s~" % (a_col.display_column_name[:2], b_col.display_column_name[:2]),
                rows_json=json.dumps(appended_rows),
                rm_dependency=None,
                manually_removable=True
            )

            if request.GET["remove_cols"] == "true":
                a_col.archived = True
                a_col.save()
                b_col.archived = True
                b_col.save()

            success = True

        except ObjectDoesNotExist as oe:
            pass

    return HttpResponse(json.dumps({
        "success": success,
    }))


def do_unionize_columns(request):
    """
    do_unionize_columns
    """
    success = False
    valid_user = token_checker.token_is_valid(request)

    if valid_user:
        proj = Project.objects.get(pk=valid_user.last_opened_project_id)
        ff = FinalFusion.objects.get(project=proj)

        ffc_group = {}
        ffcs = FinalFusionColumn.objects.filter(final_fusion=ff, archived=False).order_by("pk")

        for ffc in ffcs:
            if ffc.display_column_name not in ffc_group:
                ffc_group[ffc.display_column_name] = [ffc]
            else:
                ffc_group[ffc.display_column_name].append(ffc)

        for k in ffc_group.keys():
            appended_rows = []
            for ffc in ffc_group[k]:
                for row in json.loads(ffc.source_tq.content_json):
                    appended_rows.append(row[k])
                ffc.archived = True
                ffc.save()

            FinalFusionColumn.objects.create(
                final_fusion=ff,
                source_tq=None,
                source_column_name=k,
                display_column_name=k,
                rows_json=json.dumps(appended_rows),
                manually_removable=True
            )

        success = True

    return HttpResponse(json.dumps({
        "success": success,
    }))


def do_remove_appended(request):
    """
    do_remove_appended
    """
    success = False
    valid_user = token_checker.token_is_valid(request)

    if valid_user and "id" in request.GET and ArgsChecker.is_number(request.GET["id"]):

        try:
            app_col = FinalFusionColumn.objects.get(pk=request.GET["id"], manually_removable=True)
            app_col.archived = True
            app_col.save()
            success = True

        except ObjectDoesNotExist as oe:
            pass

    return HttpResponse(json.dumps({
        "success": success,
    }))


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


def do_check_export_button_visibility(request):
    """
    do_check_export_button_visibility
    """
    visible = False

    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        proj = Project.objects.get(pk=valid_user.last_opened_project_id)
        try:
            ff = FinalFusion.objects.get(project=proj)
            if len(FinalFusionColumn.objects.filter(final_fusion=ff, archived=False)) > 0:
                visible = True
        except ObjectDoesNotExist:
            pass
    return HttpResponse(json.dumps({"visible": visible}))


def do_count_duplicates(request):
    """
    do_check_export_button_visibility
    """
    count = 0

    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        proj = Project.objects.get(pk=valid_user.last_opened_project_id)

        try:
            ff = FinalFusion.objects.get(project=proj)
            count = ff.count_duplicates(valid_user)
        except ObjectDoesNotExist:
            pass

    return HttpResponse(json.dumps({"count": count}))


def do_apply_duplicates_settings(request):
    """
    do_apply_duplicates_settings
    """
    success = False

    valid_user = token_checker.token_is_valid(request)
    if valid_user and "setting" in request.GET and not ArgsChecker.str_is_malicious(request.GET["setting"]):

        setting = request.GET["setting"]
        proj = Project.objects.get(pk=valid_user.last_opened_project_id)
        ff = FinalFusion.objects.get(project=proj)

        if setting == "false":
            ff.ignore_duplicates = False
        elif setting == "true":
            ff.ignore_duplicates = True

        ff.save()
        success = True

    return HttpResponse(json.dumps({"success": success}))


def i_render_preview_tf(request):
    """
    i_render_preview_tf
    """
    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        return dashboard_includer.get_as_json("final_fusion/_preview.html")


def i_render_ff(request):
    """
    i_render_preview_tf
    """
    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        return dashboard_includer.get_as_json("final_fusion/_export.html")


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

            out_headers.append({
                "name": as_json["name"],
                "id": ffc_col.pk,
                "manually_removable": ffc_col.manually_removable
            })

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
    ignore_duplicates = False
    table = {"out_headers": None, "out_rows": None}

    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        table = get_preview_table(valid_user)

        proj = Project.objects.get(pk=valid_user.last_opened_project_id)
        ff = FinalFusion.objects.get(project=proj)

        if len(table["out_rows"]) > 0:
            success = True
            ignore_duplicates = ff.ignore_duplicates

    return HttpResponse(json.dumps(
        {
            "success": success,
            "ignore_duplicates": ignore_duplicates,
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
        rq.add_all_rule_modules(valid_user)
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


def render_final_fusion(request):
    """
    render_final_fusion
    """
    ret = {}
    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        proj = Project.objects.get(pk=valid_user.last_opened_project_id)
        ff = FinalFusion.objects.get(project=proj)

        table = get_preview_table(valid_user)
        rq = RuleQueue(table, changes_visible=False)
        rq.add_all_rule_modules(valid_user)
        rq.apply()

        if ff.ignore_duplicates:
            rq.table["out_rows"] = ff.remove_duplicates(rq.table["out_rows"])

        ret["project_name"] = proj.name
        ret["fusion_name"] = ff.name
        ret["content"] = rq.table["out_rows"]

    return HttpResponse(json.dumps(ret))
