import json


class DownCommandPayload:
    def __init__(self, confirmed=False, fPort=1, data=""):
        self.confirmed = confirmed
        self.fPort = fPort
        self.data = data

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
