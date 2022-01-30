import json


class PacketsPerModulation:
    def __init__(self):
        self.packets_per_modulations = []

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
