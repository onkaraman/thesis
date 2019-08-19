import json
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string


def get_as_json(template_url):
    """
    get_as_json
    """
    if ".html" not in template_url:
        raise Exception("Template URL doesn't seem legit")
    else:
        t_spl = template_url.split("/")
        template_name = t_spl[len(t_spl)-1]

        if template_name.startswith("_"):
            name_as_list = list(template_name)
            name_as_list[0] = ""
            template_name = "".join(name_as_list)

            return HttpResponse(json.dumps(
                {
                    "html": str(render_to_string(template_url)),
                    "css": settings.STATIC_URL + "css/%s" % template_name.replace("html", "css"),
                    "js": settings.STATIC_URL + "js/%s.js" % template_name.replace("html", "js"),
                }))

        else:
            raise Exception("Include template must start with an _underscore")