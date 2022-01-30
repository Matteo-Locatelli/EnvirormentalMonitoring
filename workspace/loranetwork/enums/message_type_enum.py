from enum import Enum


# Message types
class MessageTypeEnum(Enum):
    JOIN_REQUEST = (0, "JoinRequest")
    JOIN_ACCEPT = (1, "JoinAccept")
    UNCONFIRMED_DATA_UP = (2, "UnconfirmedDataUp")
    UNCONFIRMED_DATA_DOWN = (3, "UnconfirmedDataDown")
    CONFIRMED_DATA_UP = (4, "ConfirmedDataUp")
    CONFIRMED_DATA_DOWN = (5, "ConfirmedDataDown")

    def getKey(self):
        return self.value[0]

    def getName(self):
        return self.value[1]

    @staticmethod
    def findByKey(key):
        for message_type in MessageTypeEnum:
            if message_type.getKey() == key:
                return message_type

    @staticmethod
    def findByName(name):
        for message_type in MessageTypeEnum:
            if message_type.getName() == name:
                return message_type