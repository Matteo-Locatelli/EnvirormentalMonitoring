from enum import Enum


class MacCommandEnum(Enum):
    DEVICE_STATUS_REQ = (6, "DeviceStatusReq", False, 1)
    DEVICE_STATUS_ANS = (6, "DeviceStatusAns", True, 3)
    NEW_CHANNEL_REQ = (7, "NewChannelReq", False, 6)
    NEW_CHANNEL_ANS = (7, "NewChannelAns", True, 2)

    def getKey(self):
        return self.value[0]

    def getName(self):
        return self.value[1]

    def isUplink(self):
        return self.value[2]

    def getPayloadLenght(self):
        return self.value[3]

    @staticmethod
    def findByKey(key, is_uplink):
        for mac_command in MacCommandEnum:
            if mac_command.getKey() == key and mac_command.isUplink() == is_uplink:
                return mac_command

    @staticmethod
    def findByName(name, is_uplink):
        for mac_command in MacCommandEnum:
            if mac_command.getName() == name and mac_command.isUplink() == is_uplink:
                return mac_command
