import json

from payloads.info.lora_modulation import LoraModulation


class DelayTimingInfo:
    def __init__(self, delay="1s"):
        self.delay = delay


class TxInfo:
    def __init__(self, frequency=922200000, modulation="LORA", loRaModulationInfo=LoraModulation(), power=None, board=0,
                 antenna=0, timing="DELAY", delayTimingInfo=DelayTimingInfo(), context=""):
        self.frequency = frequency
        self.modulation = modulation
        self.loRaModulationInfo = loRaModulationInfo
        self.power = power
        self.board = board
        self.antenna = antenna
        self.timing = timing
        self.delayTimingInfo = delayTimingInfo
        self.context = context

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
