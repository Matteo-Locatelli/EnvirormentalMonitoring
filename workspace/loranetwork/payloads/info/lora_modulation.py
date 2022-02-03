import json


class LoraModulation:
    def __init__(self, bandwidth=125, spreadingFactor=7, codeRate="4/5", polarizationInversion=True):
        self.bandwidth = bandwidth
        self.spreadingFactor = spreadingFactor
        self.codeRate = codeRate
        self.polarizationInversion = polarizationInversion

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
