import json


class MacCommandPayload:
    def __init__(self, battery=None, margin=None, chIndex=None, freq=None, maxDR=None, minDR=None):
        # DevStatusAns
        self.battery = battery
        self.margin = margin
        # NewChannelReq
        self.chIndex = chIndex
        self.freq = freq
        self.maxDR = maxDR
        self.minDR = minDR

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class MacCommandItem:
    def __init__(self, cid=None, payload=None):
        self.cid = cid
        self.payload = payload

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
