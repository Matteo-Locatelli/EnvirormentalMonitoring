from enum import Enum


# Message types
class MessageTypeEnum(Enum):
    JOIN_REQUEST = (0, "JoinRequest", False)
    JOIN_ACCEPT = (1, "JoinAccept", True)
    UNCONFIRMED_DATA_UP = (2, "UnconfirmedDataUp", True)
    UNCONFIRMED_DATA_DOWN = (3, "UnconfirmedDataDown", False)
    CONFIRMED_DATA_UP = (4, "ConfirmedDataUp", True)
    CONFIRMED_DATA_DOWN = (5, "ConfirmedDataDown", False)

    def getKey(self):
        return self.value[0]

    def getName(self):
        return self.value[1]

    def isUplink(self):
        return self.value[2]

    @staticmethod
    def findByKey(key):
        for message_type in MessageTypeEnum:
            if message_type.getKey() == key:
                return message_type
        return None

    @staticmethod
    def findByName(name):
        for message_type in MessageTypeEnum:
            if message_type.getName() == name:
                return message_type
        return None