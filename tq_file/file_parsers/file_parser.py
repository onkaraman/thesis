from abc import ABC, abstractmethod


class FileParser(ABC):
    """
    Abstract class for inheriting parsing classes. A foreign file will be accepted
    as parsed, once it could be converted to JSON.
    """

    @abstractmethod
    def get_file_type(self):
        """
        :return: A string containing the file type the inheriting class can parse.
        """
        pass

    @abstractmethod
    def start_parse(self):
        """
        Will initiate the parsing process for the file.
        :return: The file path of the parsed file.
        """