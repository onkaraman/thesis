import json
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from tq_file.file_parsers.file_parser_json import FileParserJSON
from security.args_checker import ArgsChecker
from django.middleware.csrf import get_token as get_csrf_token
import security.token_checker as token_checker
import dashboard.includer as dashboard_includer


def delegate_to_parser(file_path, extension):
    json_parser = FileParserJSON()

    if json_parser.get_file_type() == extension:
        return json_parser.start_parse(file_path)
    return False


def do_parse_tq(request):
    """
    do_parse_tq
    """
    success = False
    msg = None

    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        if request.method == 'POST' and "file" in request.FILES:
            file = request.FILES["file"]
            task_id = request.GET["task_id"]

            if not ArgsChecker.str_is_malicious(task_id) and not ArgsChecker.str_is_malicious(file.name):
                filename_spl = file.name.split(".")
                extension = filename_spl[len(filename_spl)-1]

                file_path = "%s/%s" % (settings.TQ_UPLOAD_DIR, file.name)

                with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                json_parsed = delegate_to_parser(file_path, extension)

                if json_parsed:
                    # TODO: Save TQ, add to project, add to frontend
                else:
                    msg = "Uploaded file not supported"

    else:
        msg = "User is not valid"

    return HttpResponse(json.dumps(
        {
            "success": success,
            "msg": msg
        }))


def render_import(request):
    """
    render_import
    """
    valid_user = token_checker.token_is_valid(request)
    if valid_user:
        dic = {
            "csrf_token": get_csrf_token(request)
        }
        return dashboard_includer.get_as_json("tq_file/_import.html", template_context=dic)