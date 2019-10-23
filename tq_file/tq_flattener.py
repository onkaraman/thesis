import json
from flatten_json import flatten


class TQFlattener:
    """
    TQFlattener
    """
    @staticmethod
    def flatten(json_str):
        """
        flatten
        """
        flat = []

        for row_dict in json.loads(json_str):
            flat.append(flatten(row_dict))
        return json.dumps(flat)

    @staticmethod
    def keys_are_even(json_str):
        """
        keys_are_even
        """
        keys = []
        for j in json.loads(json_str):
            if len(keys) == 0:
                keys = j.keys()

            if j.keys() != keys:
                return False
        return True
