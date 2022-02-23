import json


class PacketsPerFrequency:
    def __init__(self):
        self

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
