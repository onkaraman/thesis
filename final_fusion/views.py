import json
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from security.args_checker import ArgsChecker
import security.token_checker as token_checker
from final_fusion_column.models import FinalFusionColumn
from final_fusion.models import FinalFusion
from project.models import Project
from rule_module.rule_queue import RuleQueue
import dashboard.includer as dashboard_includer


def do_rename(request):
    """
    Will rename a TF according to the submitted info. The name will be applied for the EF, too.
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
    Will append two columns of a TF into a new, dynamic one: A-Column + B-Column = AB-Column by appending
    B-Rows under A-Rows. If input instructs, the source A- and B-Columns will be removed from the TF
    after appending.
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
    Will append columns similar to method 'do_append_cols()'. First it will get all FFCs of the TF and then
    group all those with the same column-name into seperate lists (mapped by a dictionary). Then, it will
    append the rows of each list into new, dynamic FFCs, which will carry the same name which united the
    column names from the beginning of the process.
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
    Simply a remove function for FFCs. Since 'normal' FFCs can be removed by deselection (via TQ UI), dynamic or
    appended rows have no direct TQ-Source and therefore need to be removed manually.
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
    Will return the shortened column vars for scripting modules to the UI. See FinalFusion-Model for more details.
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
    The export-button for the final fusion will only be visible in the UI, if the TF contains at least one FFC
    (selected into it).
    """
    visible = False
    tf_name = ""

    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        if valid_user.last_opened_project_id:
            proj = Project.objects.get(pk=valid_user.last_opened_project_id)
            try:
                ff = FinalFusion.objects.get(project=proj)
                ffcs = FinalFusionColumn.objects.filter(final_fusion=ff, archived=False)
                if len(ffcs) > 0:
                    visible = True
                    tf_name = ffcs[0].final_fusion.name
            except ObjectDoesNotExist:
                pass
    return HttpResponse(json.dumps({
        "visible": visible,
        "tf_name": tf_name
    }))


def do_count_duplicates(request):
    """
    Will return the duplicate count of the TF. See model for more info.
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
    Will apply whether duplicates should be exported (in EF) or not, by saving that setting to the FF-Model itself.
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
    Will provide inclusion data of the preview UI for the frontend.
    """
    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        return dashboard_includer.get_as_json("final_fusion/_preview.html")


def i_render_ff(request):
    """
    Will provide inclusion data of the export UI for the frontend.
    """
    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        return dashboard_includer.get_as_json("final_fusion/_export.html")


def get_preview_table(user_profile):
    """
    Will put all models together to render a cohesive in-progress final fusion table.
    If a dynamic FFC doesn't have its creator-rule module any longer, it should be archived and thereby
    not rendered anymore
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
                ffc_col.display_column_name not in ffc_col.rm_dependency.depending_dynamic_columns():
            ffc_col.archived = True
            ffc_col.save()
        else:
            as_json = ffc_col.get_as_json()

            out_headers.append({
                "name": as_json["name"],
                "id": ffc_col.pk,
                "dynamic": as_json["dynamic"],
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
    Will return the in-progress table of the final fusion, the TF, without activated rule modules.
    Will also provide metadata for further frontend display options.
    """
    success = False
    ignore_duplicates = False
    table = {"out_headers": None, "out_rows": None}
    ff_name = ""

    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        table = get_preview_table(valid_user)

        proj = Project.objects.get(pk=valid_user.last_opened_project_id)
        ff = FinalFusion.objects.get(project=proj)
        ff_name = ff.name

        if len(table["out_rows"]) > 0:
            success = True
            ignore_duplicates = ff.ignore_duplicates

    return HttpResponse(json.dumps(
        {
            "success": success,
            "ff_name": ff_name,
            "ignore_duplicates": ignore_duplicates,
            "headers": table["out_headers"],
            "rows": table["out_rows"]
        }))


def render_preview_table_with_rm(request):
    """
    Will return render data of the TF, in which added rules modules are applied (changes visible).
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
    Will render table data of the FF/Export, in which rule module changes are applied (changes not visible).
    """
    ret = {}
    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        proj = Project.objects.get(pk=valid_user.last_opened_project_id)
        ff = FinalFusion.objects.get(project=proj)

        table = get_preview_table(valid_user)
        rq = RuleQueue(table, changes_visible=False)
        rq.add_all_rule_modules(valid_user)
        rq.apply(export=True)

        if ff.ignore_duplicates:
            rq.table["out_rows"] = ff.remove_duplicates(rq.table["out_rows"])

        ret["project_name"] = proj.name
        ret["fusion_name"] = ff.name
        ret["content"] = rq.table["out_rows"]

    return HttpResponse(json.dumps(ret))
