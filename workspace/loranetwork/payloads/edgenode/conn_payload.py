import json


class ConnPayload:
    def __init__(self, gatewayID="", state=""):
        self.gatewayID = gatewayID  # encoded base64 standard
        self.state = state

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
