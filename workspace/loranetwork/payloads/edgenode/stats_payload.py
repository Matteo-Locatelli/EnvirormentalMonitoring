import json

from payloads.info.packets_per_frequency import PacketsPerFrequency
from payloads.info.packets_per_status import PacketsPerStatus


class Metadata:
    def __init__(self):
        self

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class StatsPayload:
    def __init__(self, id_gateway="", ip="", time="", config_version="", rx_packets_received=0, rx_packets_received_ok=0,
                 tx_packets_received=0, tx_packets_emitted=0, stats_id="", location=None, metadata=Metadata(),
                 tx_packets_per_frequency=PacketsPerFrequency(), rx_packets_per_frequency=PacketsPerFrequency(),
                 tx_packets_per_modulation=[], rx_packets_per_modulation=[],
                 tx_packets_per_status=PacketsPerStatus()):
        self.gatewayID = id_gateway  # encoded base64 standard
        self.ip = ip
        self.time = time  # format datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.configVersion = config_version
        self.rxPacketsReceived = rx_packets_received
        self.rxPacketsReceivedOK = rx_packets_received_ok
        self.txPacketsReceived = tx_packets_received
        self.txPacketsEmitted = tx_packets_emitted
        self.statsID = stats_id
        self.location = location

        # optional fields
        self.metaData = metadata
        self.txPacketsPerFrequency = tx_packets_per_frequency
        self.rxPacketsPerFrequency = rx_packets_per_frequency
        self.txPacketsPerModulation = tx_packets_per_modulation
        self.rxPacketsPerModulation = rx_packets_per_modulation
        self.txPacketsPerStatus = tx_packets_per_status

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
