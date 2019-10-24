import json
import math
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
            for k in list(row):
                if str(k) == "nan" and math.isnan(k):
                    return None

            zipped = dict(zip(columns, list(row)))
            parsable.append(zipped)

        return json.dumps(parsable)

    @staticmethod
    def get_sheet_names(file_path):
        """
        get_sheet_names
        """
        try:
            return pd.ExcelFile(file_path).sheet_names
        except Exception:
            return None
