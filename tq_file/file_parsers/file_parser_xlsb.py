import json
import pandas as pd
from .file_parser import FileParser
from pyxlsb import open_workbook as open_xlsb


class FileParserXLSB(FileParser):
    """
    FileParserXLSB
    """

    def handles_file_type(self, extension):
        return extension == "xlsb"

    def start_parse(self, file_path, data=None):
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

    def get_sheet_names(self, file_path):
        with open_xlsb(file_path) as wb:
            return wb.sheets