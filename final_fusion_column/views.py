import json
from django.http import HttpResponse
import security.token_checker as token_checker
from security.args_checker import ArgsChecker
from .models import FinalFusionColumn
from rule_module.models import RuleModule


def do_rename(request):
    """
    do_rename
    """
    success = False
    valid_user = token_checker.token_is_valid(request)

    if valid_user and "id" in request.GET and ArgsChecker.is_number(request.GET["id"]) \
            and "name" in request.GET and not ArgsChecker.str_is_malicious(request.GET["name"]):
        try:
            name = request.GET["name"]
            name = name.replace("(", "[");
            name = name.replace(")", "]");

            ffc = FinalFusionColumn.objects.get(pk=request.GET["id"], archived=False)
            ffc.display_column_name = name
            ffc.save()
            success = True

            # Check if this FFC is a dynamic column of
            if ffc.rm_dependency:
                rm = ffc.rm_dependency
                then_cases = json.loads(rm.then_cases)
                for tc in then_cases:
                    if tc["id"] == ffc.pk:
                        tc["ffc_name"] = request.GET["name"]
                        break
                rm.then_cases = json.dumps(then_cases)
                rm.save()

        except ImportError:
            pass

    return HttpResponse(json.dumps({"success": success}))
