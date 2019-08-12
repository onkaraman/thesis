class StringStripper:
    """
    Offers methods to remove dangerous characters from strings.
    """

    @staticmethod
    def remove_malicious(string):
        """
        Will remove "; { } < >"
        :param string: Possibly dirty string to clean.
        :return: String without coding characters.
        """
        string = string.replace(";", ",")
        string = string.replace("{", "(")
        string = string.replace("}", ")")
        string = string.replace(">", "")
        string = string.replace("<", "")
        string = string.replace("throw", "")
        string = string.replace("raise", "")
        string = string.replace("*", "")
        string = string.replace("null", "")
        string = string.replace("Null", "")
        string = string.replace("None", "")
        string = string.replace("none", "")
        string = string.replace("(\"", "")
        string = string.replace("\")", "")
        string = string.replace("('", "")
        string = string.replace("')", "")
        string = string.replace("error", "")
        string = string.replace("Error", "")
        string = string.replace("exception", "")
        string = string.replace("Exception", "")
        return string
