import os
import json
from django.conf import settings
from .file_parser import FileParser


class FileParserJSON(FileParser):
    """
    FileParserJSON
    """
    def handles_file_type(self, extension):
        return extension == "json"

    def start_parse(self, file_path, data=None):
        file_ = open(os.path.join(settings.BASE_DIR, file_path))
        parsable = json.loads(file_.read())

        return json.dumps(parsable)
