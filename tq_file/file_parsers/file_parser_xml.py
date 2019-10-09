import json
import xmltodict
from .file_parser import FileParser


class FileParserXML(FileParser):
    """
    FileParserXML
    """
    def get_file_type(self):
        return "xml"

    def start_parse(self, file_path):
        with open(file_path) as fd:
            doc = xmltodict.parse(fd.read())
            parsable = []
            for odict in doc["dataset"]["record"]:
                d = {}
                for k in odict.keys():
                    d[k] = odict[k]
                parsable.append(d)

            return json.dumps(parsable)
