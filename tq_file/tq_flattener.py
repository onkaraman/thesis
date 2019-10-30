import json
from flatten_json import flatten


class TQFlattener:
    """
    This class will flatten parsed JSON-TQs by moving all keys to the first level of the structure.
    """
    @staticmethod
    def flatten(json_str):
        """
        :return The flattened JSON.
        """
        flat = []

        for row_dict in json.loads(json_str):
            flat.append(flatten(row_dict))
        return json.dumps(flat)

    @staticmethod
    def keys_are_even(json_str):
        """
        :return True if every row of the TQ has exactly the same keys (none missing or unknown).
        """
        keys = []
        for j in json.loads(json_str):
            if len(keys) == 0:
                keys = j.keys()

            if j.keys() != keys:
                return False
        return True
