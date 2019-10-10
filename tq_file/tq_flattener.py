import json
from flatten_json import flatten


class TQFlattener:
    """
    TQFlattener
    """
    def flatten(self, json_str):
        """
        flatten
        """
        flat = []

        for row_dict in json.loads(json_str):
            flat.append(flatten(row_dict))
        return json.dumps(flat)