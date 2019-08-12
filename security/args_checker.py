from security.string_stripper import StringStripper


class ArgsChecker:
    """
    Offers methods to check arguments coming from GET for validation.
    """
    @staticmethod
    def number_within_range(number, min, max):
        """
        Will return True if the passed number is within the specified range.
        :param number: Number to check.
        """
        try:
            if min <= number <= max:
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def is_number(data, max_length=0):
        try:
            if data.isdigit():
                if max_length > 0:
                    if len(str(StringStripper.remove_malicious(data))) <= max_length:
                        return True
                    return False
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def string_must_contain(substring, data, min_length=0):
        if StringStripper.remove_malicious(substring) \
                in data or substring.lower() in data or substring.upper() in data:
            if min_length > 0:
                if len(data) >= min_length:
                    return True
                return False
            return True
        return False

    @staticmethod
    def str_is_malicious(data):
        if data != StringStripper.remove_malicious(data):
            return True
        return False

    @staticmethod
    def string_contains_one_of(string, opt_list):
        for l in opt_list:
            if string == l:
                return True
        return False
