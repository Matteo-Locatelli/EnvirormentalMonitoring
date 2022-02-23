import json


class DownlinkConfigurationPayload:
    def __init__(self, timestosend=0, timetoreceive=0):
        self.timetosend = timestosend
        self.timetoreceive = timetoreceive

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)
