import json
from django.conf import settings
from django.http import HttpResponse
from django.middleware.csrf import get_token as get_csrf_token
from tq_file.file_parsers.file_parser_json import FileParserJSON
from tq_file.models import TQFile
from project.models import Project
from security.args_checker import ArgsChecker
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
                extension = filename_spl[len(filename_spl) - 1]

                file_path = "%s/%s" % (settings.TQ_UPLOAD_DIR, file.name)

                with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                json_parsed = delegate_to_parser(file_path, extension)

                if json_parsed:
                    tq = TQFile.objects.create(
                        project=valid_user.get_project(),
                        source_file_name=file.name,
                        display_file_name=file.name,
                        content_json=json_parsed
                    )
                    success = True
                else:
                    msg = "Uploaded file not supported"

    else:
        msg = "User is not valid"

    return HttpResponse(json.dumps(
        {
            "success": success,
            "msg": msg
        }))


def render_tqs(request):
    """
    render_tqs
    """
    success = False
    tq_list = []

    valid_user = token_checker.token_is_valid(request)

    if valid_user:
        project = Project.objects.get(pk=valid_user.last_opened_project_id)
        for tq in TQFile.objects.filter(project=project):
            tq_list.append({
                "name": tq.display_file_name
            })
        success = True

    return HttpResponse(json.dumps(
        {
            "success": success,
            "tqs": tq_list,
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
