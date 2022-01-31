import json


class MacCommandPayload:
    def __init__(self, battery=None, margin=None):
        self.battery = battery
        self.margin = margin

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class MacCommandItem:
    def __init__(self, cid=None, payload=None):
        self.cid = cid
        self.payload = payload

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
