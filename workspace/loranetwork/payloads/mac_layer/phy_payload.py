import json


class MHDR:
    def __init__(self, mType=None, major=None):
        self.mType = mType
        self.major = major

    def __eq__(self, other):
        if not isinstance(other, PhyPayload):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.mType.__eq__(other.mType) and self.major.__eq__(other.major)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class Frame:

    def __init__(self, bytes_data=None):
        if type(bytes_data) is bytes:
            self.bytes = bytes_data.decode()
        else:
            self.bytes = bytes_data

    def __eq__(self, other):
        if not isinstance(other, PhyPayload):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.adr.__eq__(other.adr)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class FCTRL:
    def __init__(self, data=bytearray()):
        if (len(data) > 0):
            self.adr = data[0] & 0x80 != 0
            self.adrAckReq = data[0] & 0x40 != 0
            self.ack = data[0] & 0x20 != 0
            self.classB = data[0] & 0x10 != 0
            self.fPending = data[0] & 0x10 != 0
            self.fOptsLen = data[0] & 0x0f
        else:
            self.adr = False
            self.adrAckReq = False
            self.ack = False
            self.classB = False
            self.fPending = False
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
            self.adr, self.adrAckReq, self.ack, self.classB, self.fPending, self.fOptsLen)

    def __eq__(self, other):
        if not isinstance(other, PhyPayload):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.adr.__eq__(other.adr) and self.adrAckReq.__eq__(other.adrAckReq) and \
               self.ack.__eq__(other.ack) and self.classB.__eq__(other.classB) and \
               self.fPending.__eq__(other.fPending) and self.fOptsLen.__eq__(other.fOptsLen)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class FHDR:
    def __init__(self):
        self.devAddr = None
        self.fCtrl = FCTRL()
        self.fCnt = None
        self.fOpts = None

    def __eq__(self, other):
        if not isinstance(other, PhyPayload):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.devAddr.__eq__(other.devAddr) and self.fCtrl.__eq__(other.fCtrl) and \
               self.fCnt.__eq__(other.fCnt) and self.fOpts.__eq__(other.fOpts)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)


class MacPayload:
    def __init__(self):
        self.fhdr = FHDR()
        self.fPort = None
        self.frmPayload = []
        self.joinEUI = None
        self.devEUI = None
        self.devNonce = None
        self.bytes = None

    def __eq__(self, other):
        if not isinstance(other, PhyPayload):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.fhdr.__eq__(other.fhdr) and self.fPort.__eq__(other.fPort) and \
               self.frmPayload.__eq__(other.frmPayload) and self.joinEUI.__eq__(other.joinEUI) and \
               self.devEUI.__eq__(other.devEUI) and self.devNonce.__eq__(other.devNonce) and \
               self.bytes.__eq__(other.bytes)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class PhyPayload:
    def __init__(self):
        self.mhdr = MHDR()
        self.macPayload = MacPayload()
        self.mic = None

    def __eq__(self, other):
        if not isinstance(other, PhyPayload):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.mhdr.__eq__(other.mhdr) and self.macPayload.__eq__(other.macPayload) and self.mic.__eq__(other.mic)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
