import json


class TxAckPayload:
    def __init__(self, gatewayID="", token="", downlink_id=""):
        self.gatewayID = gatewayID
        self.token = token
        self.items = []
        self.downlink_id = downlink_id

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
