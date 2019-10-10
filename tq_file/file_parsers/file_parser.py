from abc import ABC, abstractmethod


class FileParser(ABC):
    """
    Abstract class for inheriting parsing classes. A foreign file will be accepted
    as parsed, once it could be converted to JSON.
    """

    @abstractmethod
    def handles_file_type(self, extension):
        """
        :return: A string containing the file type (extension format)  the inheriting class can parse.
        """
        raise Exception("Method not implemented.")

    @abstractmethod
    def start_parse(self, file_path, data=None):
        """
        Will initiate the parsing process for the file.
        :return: The file path of the parsed file.
        """
        raise Exception("Method not implemented.")