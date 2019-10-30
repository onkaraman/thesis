import json
import xmltodict
from .file_parser import FileParser


class FileParserXML(FileParser):
    """
    Concretization of the abstrtact class for XML-Formats.
    """
    def handles_file_type(self, extension):
        return extension == "xml"

    def start_parse(self, file_path, data=None):
        """
        Will make use of a lib to parse the XML to a list of dictionaries.
        Will then pick that list apart to get a list of pure entries to turn into a JSON.
        """
        with open(file_path) as fd:
            try:
                doc = xmltodict.parse(fd.read())
                parsable = []
                for odict in doc["dataset"]["record"]:
                    d = {}
                    for k in odict.keys():
                        d[k] = odict[k]
                    parsable.append(d)

                return json.dumps(parsable)
            except Exception:
                return None
