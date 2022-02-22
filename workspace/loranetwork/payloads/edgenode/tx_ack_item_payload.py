import json


class TxAckItemPayload:
    def __init__(self, status=""):
        self.status = status

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
