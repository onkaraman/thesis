import json
from django.http import HttpResponse
import security.token_checker as token_checker
from security.args_checker import ArgsChecker
from .models import FinalFusionColumn


def do_rename(request):
    """
    do_rename
    """
    success = False
    valid_user = token_checker.token_is_valid(request)

    if valid_user and "id" in request.GET and ArgsChecker.is_number(request.GET["id"]) \
            and "name" in request.GET and not ArgsChecker.str_is_malicious(request.GET["name"]):
        try:
            ffc = FinalFusionColumn.objects.get(pk=request.GET["id"], archived=False)
            ffc.display_column_name = request.GET["name"]
            ffc.save()
            success = True
        except ImportError:
            pass

    return HttpResponse(json.dumps({"success": success}))
