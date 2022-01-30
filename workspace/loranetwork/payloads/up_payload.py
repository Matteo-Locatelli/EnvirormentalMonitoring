import json

from payloads.info.rx_info import RxInfo
from payloads.info.tx_info import TxInfo


class UpPayload:
    def __init__(self, phyPayload="", txInfo=TxInfo(), rxInfo=RxInfo()):
        self.phyPayload = phyPayload
        self.txInfo = txInfo
        self.rxInfo = rxInfo

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
