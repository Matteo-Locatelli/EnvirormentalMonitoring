import json

from payloads.info.packets_per_frequency import PacketsPerFrequency
from payloads.info.packets_per_modulation import PacketsPerModulation
from payloads.info.packets_per_status import PacketsPerStatus


class Metadata:
    def __init__(self):
        self

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class StatsPayload:
    def __init__(self, id_gateway="", ip="", time="", configVersion="", rxPacketsReceived=0, rxPacketsReceivedOK=0,
                 txPacketsReceived=0, txPacketsEmitted=0, statsID="", location=None, metaData=Metadata(),
                 txPacketsPerFrequency=PacketsPerFrequency(), rxPacketsPerFrequency=PacketsPerFrequency(),
                 txPacketsPerModulation=PacketsPerModulation(), rxPacketsPerModulation=PacketsPerModulation(),
                 txPacketsPerStatus=PacketsPerStatus()):
        self.gatewayID = id_gateway # encoded base64 standard
        self.ip = ip
        self.time = time #format datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.configVersion = configVersion
        self.rxPacketsReceived = rxPacketsReceived
        self.rxPacketsReceivedOK = rxPacketsReceivedOK
        self.txPacketsReceived = txPacketsReceived
        self.txPacketsEmitted = txPacketsEmitted
        self.statsID = statsID
        self.location = location

        # optional fields
        self.metaData = metaData
        self.txPacketsPerFrequency = txPacketsPerFrequency
        self.rxPacketsPerFrequency = rxPacketsPerFrequency
        self.txPacketsPerModulation = txPacketsPerModulation
        self.rxPacketsPerModulation = rxPacketsPerModulation
        self.txPacketsPerStatus = txPacketsPerStatus

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
