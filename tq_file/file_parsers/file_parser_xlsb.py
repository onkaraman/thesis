import json
import pandas as pd
from .file_parser import FileParser
from pyxlsb import open_workbook as open_xlsb


class FileParserXLSB(FileParser):
    """
    Concretization of the abstrtact class for XLSB-Formats.
    """

    def handles_file_type(self, extension):
        return extension == "xlsb"

    def start_parse(self, file_path, data=None):
        """
        Will first take all columns of the excel and will then read each row.
        Then it will create a dictionary for each row by zipping column names and row entries.
        Each row dict will be added to list, which in turn will be returned as a JSON.
        """
        with open_xlsb(file_path) as wb:

            cols = []
            data_frame = []
            with wb.get_sheet(data) as sheet:
                for row in sheet.rows():
                    l = [item.v for item in row]
                    if not cols:
                        cols = l
                    data_frame.append(l)

        data_frame = pd.DataFrame(data_frame[1:], columns=data_frame[0])
        data = data_frame.to_dict("split")["data"]

        parsable = []
        for d in data:
            parsable.append(dict(zip(cols, d)))

        return json.dumps(parsable)

    @staticmethod
    def get_sheet_names(file_path):
        """
        Will return the list of sheet names this Excel is containing.
        """
        with open_xlsb(file_path) as wb:
            return wb.sheets
