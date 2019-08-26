import os
import json
from django.conf import settings
from .file_parser import FileParser
from tq_file.models import TQFile


class FileParserJSON(FileParser):
    """
    FileParserJSON
    """
    def get_file_type(self):
        return "json"

    def start_parse(self, file_path):
        file_ = open(os.path.join(settings.BASE_DIR, file_path))
        parsable = json.loads(file_.read())

        return json.dumps(parsable)
