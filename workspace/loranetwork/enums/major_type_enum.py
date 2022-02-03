from enum import Enum


class MajorTypeEnum(Enum):
    LoRaWANR1 = (0, "LoRaWANR1")
    LoRaWANR0 = (1, "LoRaWANR0")

    def getKey(self):
        return self.value[0]

    def getName(self):
        return self.value[1]

    @staticmethod
    def findByKey(key):
        for major_type in MajorTypeEnum:
            if major_type.getKey() == key:
                return major_type
        return None

    @staticmethod
    def findByName(name):
        for major_type in MajorTypeEnum:
            if major_type.getName() == name:
                return major_type
        return None