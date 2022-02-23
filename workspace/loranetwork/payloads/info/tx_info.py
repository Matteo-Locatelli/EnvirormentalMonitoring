import json

from payloads.info.lora_modulation import LoraModulation


class DelayTimingInfo:
    def __init__(self, delay="1s"):
        self.delay = delay


class TxInfo:
    def __init__(self, frequency=868100000, modulation="LORA", lo_ra_modulation_info=LoraModulation(), power=14, board=0,
                 antenna=0, timing="DELAY", delay_timing_info=DelayTimingInfo(), context=""):
        self.frequency = frequency
        self.modulation = modulation
        self.loRaModulationInfo = lo_ra_modulation_info
        self.power = power
        self.board = board
        self.antenna = antenna
        self.timing = timing
        self.delayTimingInfo = delay_timing_info
        self.context = context

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
