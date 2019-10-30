import os
import json
from json.decoder import JSONDecodeError
from django.conf import settings
from .file_parser import FileParser


class FileParserJSON(FileParser):
    """
    Concretization of the abstrtact class for JSON-Formats.
    """
    def handles_file_type(self, extension):
        return extension == "json"

    def start_parse(self, file_path, data=None):
        """
        Will just take the uploaded JSON and parse it over.
        """
        file_ = open(os.path.join(settings.BASE_DIR, file_path), encoding="UTF-8")
        try:
            parsable = json.loads(file_.read())
        except JSONDecodeError:
            return None

        return json.dumps(parsable)
