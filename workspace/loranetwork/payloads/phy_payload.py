import json


class MHDR:
    def __init__(self, mType=None, major=None):
        self.mType = mType
        self.major = major

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class Frame:

    def __init__(self, bytes_data=None):
        if type(bytes_data) is bytes:
            self.bytes = bytes_data.decode()
        else:
            self.bytes = bytes_data

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class FRMPayload:
    def __init__(self):
        self.frames = []

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class FOpts:
    def __init__(self):
        self

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class FCTRL:
    def __init__(self, data=bytearray()):
        if (len(data) > 0):
            self.ADR = data[0] & 0x80 != 0
            self.ADRACKReq = data[0] & 0x40 != 0
            self.ACK = data[0] & 0x20 != 0
            self.ClassB = data[0] & 0x10 != 0
            self.FPending = data[0] & 0x10 != 0
            self.fOptsLen = data[0] & 0x0f
        else:
            self.ADR = False
            self.ADRACKReq = False
            self.ACK = False
            self.ClassB = False
            self.FPending = False
            self.fOptsLen = 0

    def getByte(self):
        byte = 0x00
        byte = byte | (int(self.ADR) * 0x80)
        byte = byte | (int(self.ADRACKReq) * 0x40)
        byte = byte | (int(self.ACK) * 0x20)
        byte = byte | (int(self.ClassB) * 0x10)
        byte = byte | (int(self.FPending) * 0x10)
        if (byte & 0x0f) != self.fOptsLen:
            raise Exception("Something is wrong")
        return byte.to_bytes(1, 'big')

    def getString(self):
        return "ADR:%02s ADRACKReq:%02s ACK:%02s ClassB:%02s FPending:%02s fOptsLen:%01x" % (
            self.ADR, self.ADRACKReq, self.ACK, self.ClassB, self.FPending, self.fOptsLen)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class FHDR:
    def __init__(self):
        self.devAddr = None
        self.fCtrl = FCTRL()
        self.fCnt = None

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)


class MacPayload:
    def __init__(self):
        self.fhdr = FHDR()
        self.fPort = None
        self.frmPayload = FRMPayload()
        self.joinEUI = None
        self.devEUI = None
        self.devNonce = None
        self.bytes = None

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class PhyPayload:
    def __init__(self):
        self.mhdr = MHDR()
        self.macPayload = MacPayload()
        self.mic = None

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
