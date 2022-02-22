from payloads.info.rx_info import RxInfo
from payloads.info.tx_info import TxInfo


class JoinEventPayload:
    def __init__(self, applicationID="", deviceName="", devEUI="", devAddr="", rxInfo=RxInfo(), txInfo=TxInfo(),
                 dr=0, publishedAt=""):
        self.applicationID = applicationID
        self.deviceName = deviceName
        self.devEUI = devEUI
        self.devAddr = devAddr
        self.rxInfo = rxInfo
        self.txInfo = txInfo
        self.dr = dr
        self.publishedAt = publishedAt