import json
import math
import pandas as pd
from .file_parser import FileParser


class FileParserXLSx(FileParser):
    """
    Concretization of the abstrtact class for XLSX-Formats.
    """
    def handles_file_type(self, extension):
        return "xls" == extension or "xlsx" == extension

    def start_parse(self, file_path, data=None):
        """
        Will first take all columns of the excel and will then read each row.
        Then it will create a dictionary for each row by zipping column names and row entries.
        Each row dict will be added to list, which in turn will be returned as a JSON.
        """
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
        Will return the list of sheet names this Excel is containing.
        """
        try:
            return pd.ExcelFile(file_path).sheet_names
        except Exception:
            return None
