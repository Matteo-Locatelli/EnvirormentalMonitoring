import json

from payloads.info.tx_info import TxInfo


class DownItem:
    def __init__(self, phyPayload="", txInfo=TxInfo()):
        self.phyPayload = phyPayload
        self.txInfo = txInfo

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class DownPayload:
    def __init__(self, phyPayload="", txInfo=TxInfo(), token=None, downlinkID="", items=[], gatewayID=""):
        self.phyPayload = phyPayload
        self.txInfo = txInfo
        self.token = token
        self.downlinkID = downlinkID
        self.items = items  # list of DownItem
        self.gatewayID = gatewayID

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
