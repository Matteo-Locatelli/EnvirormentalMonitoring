import json


class LoraModulation:
    def __init__(self, bandwidth=125, spreading_factor=7, code_rate="4/5", polarization_inversion=True):
        self.bandwidth = bandwidth
        self.spreadingFactor = spreading_factor
        self.codeRate = code_rate
        self.polarizationInversion = polarization_inversion

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
