import json
import pandas as pd
from .file_parser import FileParser


class FileParserXLSx(FileParser):
    """
    FileParserXLSx
    """
    def handles_file_type(self, extension):
        return "xls" == extension or "xlsx" == extension

    def start_parse(self, file_path):
        excel = pd.read_excel(file_path, sheet_name=None)["data"]
        columns = list(excel.columns)
        rows = list(excel.values)

        parsable = []
        for row in rows:
            zipped = dict(zip(columns, list(row)))
            parsable.append(zipped)

        return json.dumps(parsable)
