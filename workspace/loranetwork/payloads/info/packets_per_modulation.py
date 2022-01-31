import json

from payloads.info.lora_modulation import LoraModulation


class PacketsPerModulation:
    def __init__(self, modulation=LoraModulation(), count=0):
        self.modulation = modulation
        self.count = count

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
