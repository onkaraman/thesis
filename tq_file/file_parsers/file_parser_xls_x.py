import json
import pandas as pd
from .file_parser import FileParser


class FileParserXLSx(FileParser):
    """
    FileParserXLSx
    """
    def handles_file_type(self, extension):
        return "xls" == extension or "xlsx" == extension

    def start_parse(self, file_path, data=None):
        excel = pd.read_excel(file_path, sheet_name=data)
        columns = list(excel.columns)
        rows = list(excel.values)

        parsable = []
        for row in rows:
            zipped = dict(zip(columns, list(row)))
            parsable.append(zipped)

        return json.dumps(parsable)

    def get_sheet_names(self, file_path):
        return pd.ExcelFile(file_path).sheet_names
