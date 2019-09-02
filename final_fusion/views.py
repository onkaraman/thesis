import json
from django.shortcuts import render
from django.http import HttpResponse
from security.args_checker import ArgsChecker
import security.token_checker as token_checker
from tq_file.models import TQFile
from final_fusion_column.models import FinalFusionColumn
from final_fusion.models import FinalFusion
from project.models import Project


def do_add_column(request):
    """
    do_add_column
    """
    success = False

    valid_user = token_checker.token_is_valid(request)
    if valid_user and "tq_id" in request.GET and ArgsChecker.is_number(request.GET["tq_id"]) \
            and "col_name" in request.GET and not ArgsChecker.str_is_malicious(request.GET["col_name"]):
        tq_id = request.GET["tq_id"]
        col_name = request.GET["col_name"]

        tq = TQFile.objects.get(pk=tq_id)
        col = tq.get_column(col_name)

        ffc = FinalFusionColumn.objects.create(
            final_fusion=FinalFusion.objects.get(project=Project.objects.get(pk=valid_user.last_opened_project_id)),
            source_column_name=col_name,
            display_column_name=col_name,
            rows_json=json.dumps(col)
        )

        success = True

    return HttpResponse(json.dumps({"success": success}))
