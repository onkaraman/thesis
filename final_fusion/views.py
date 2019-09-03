import json
from django.shortcuts import render
from django.http import HttpResponse
from security.args_checker import ArgsChecker
import security.token_checker as token_checker
from tq_file.models import TQFile
from final_fusion_column.models import FinalFusionColumn
from final_fusion.models import FinalFusion
from project.models import Project


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
