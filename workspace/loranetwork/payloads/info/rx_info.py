import json

from enums.crc_status_enum import CRCStatusEnum


class RxInfo:
    def __init__(self, gatewayID="", time="", timeSinceGPSEpoch=None, rssi=-60, loRaSNR=7, channel=0,
                 rfChain=0, board=0, antenna=0, location=None, fineTimestampType="NONE", context="", uplinkID="",
                 crcStatus=CRCStatusEnum.NO_CRC.name):
        self.gatewayID = gatewayID  # encoded base64 standard
        self.time = time  # set only when there is a GPS time source
        self.timeSinceGPSEpoch = timeSinceGPSEpoch  # set only when there is a GPS time source(timestamp 23bit)
        self.rssi = rssi
        self.loRaSNR = loRaSNR
        self.channel = channel
        self.rfChain = rfChain
        self.board = board
        self.antenna = antenna
        self.location = location
        self.fineTimestampType = fineTimestampType
        self.context = context
        self.uplinkID = uplinkID
        self.crcStatus = crcStatus

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
