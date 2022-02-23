import json

from enums.crc_status_enum import CRCStatusEnum


class RxInfo:
    def __init__(self, gateway_id="", time="", time_since_gps_epoch=None, rssi=-60, lo_ra_snr=7, channel=0,
                 rf_chain=0, board=0, antenna=0, location=None, fine_timestamp_type="NONE", context="", uplink_id="",
                 crc_status=CRCStatusEnum.NO_CRC.name):
        self.gatewayID = gateway_id  # encoded base64 standard
        self.time = time  # set only when there is a GPS time source
        self.timeSinceGPSEpoch = time_since_gps_epoch  # set only when there is a GPS time source(timestamp 23bit)
        self.rssi = rssi
        self.loRaSNR = lo_ra_snr
        self.channel = channel
        self.rfChain = rf_chain
        self.board = board
        self.antenna = antenna
        self.location = location
        self.fineTimestampType = fine_timestamp_type
        self.context = context
        self.uplinkID = uplink_id
        self.crcStatus = crc_status

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
