from types import SimpleNamespace
import json
import jsonpickle
from json import JSONEncoder
import base64
import struct
from PhyPayload import *

MTYPE_JOIN_REQUEST = 0
MTYPE_JOIN_ACCEPT = 1
MTYPE_UNCONFIRMED_DATA_UP = 2
MTYPE_UNCONFIRMED_DATA_DOWN = 3
MTYPE_CONFIRMED_DATA_UP = 4
MTYPE_CONFIRMED_DATA_DOWN = 5
MTYPE_RFU = 6
MTYPE_PROPRIETARY = 7
MAJOR_LoRaWANR1 = 0
MAJOR_LoRaWANR0 = 1


def MType(byte):
    return struct.unpack("B", byte)[0] >> 5


def Major(byte):
    return struct.unpack("B", byte)[0] & 0x03


def decodeDevAddr(data):
    return data[::-1]


def decodeMic(data):
    return data[::-1]


def decodeFHDR(data):
    FHdr = FHDR()
    FHdr.devAddr = decodeDevAddr(data[0:4]).hex()
    FHdr.fCtrl = FCTRL(data[4:5])
    fCnt_byte = bytearray(6)
    fCnt_byte += data[5:7]
    FHdr.fCnt = int.from_bytes(fCnt_byte, 'big')
    return FHdr


def decodePhyPayload(phy_payload_encoded):
    data = base64.b64decode(phy_payload_encoded)

    phyPayload = PhyPayload()
    mhdrByte = data[0].to_bytes(1, 'big')
    macPayloadByte = data[1:-4]
    mic = data[-4:]
    assert (len(data) == len(mhdrByte) + len(macPayloadByte) + len(mic))

    mtype = MType(mhdrByte)
    major = Major(mhdrByte)
    phyPayload.mhdr = MHDR()

    if major != MAJOR_LoRaWANR1:
        raise Exception("Lorawan version must be 1.0 or 1.1")
    else:
        phyPayload.mhdr.major = "LoRaWANR1"

    if mtype == MTYPE_JOIN_REQUEST:
        print(" *** Join-request")
        joinEUI = data[1:9]
        devEUI = data[9:17]
        nonce = data[17:19]

        phyPayload.macPayload = MacPayload()
        joinEUI = joinEUI[::-1]
        devEUI = devEUI[::-1]
        nonce = nonce[::-1]
        phyPayload.mhdr.mType = "JoinRequest"
        phyPayload.macPayload.joinEUI = joinEUI.hex()
        phyPayload.macPayload.devEUI = devEUI.hex()
        phyPayload.macPayload.devNonce = int.from_bytes(nonce, 'big')
        phyPayload.mic = mic.hex()
        print("  JoinEUI: %s" % joinEUI.hex())
        print("  DevEUI: %s" % devEUI.hex())
        print("  Nonce:  %s" % nonce.hex())
        print("  MIC: %s" % mic.hex())
    elif mtype == MTYPE_JOIN_ACCEPT:
        print(" *** Join Accept")
        phyPayload.mhdr.mType = "JoinAccept"
        phyPayload.macPayload = MacPayload()
        phyPayload.macPayload.bytes = base64.b64encode(macPayloadByte).decode()
        phyPayload.mic = mic.hex()
        print("  Data base64 encoded: %s" % base64.b64encode(macPayloadByte))
    elif mtype == MTYPE_UNCONFIRMED_DATA_UP or mtype == MTYPE_CONFIRMED_DATA_UP or mtype == MTYPE_CONFIRMED_DATA_DOWN or mtype == MTYPE_UNCONFIRMED_DATA_DOWN:
        macPayload = MacPayload()

        fCtrl = FCTRL(macPayloadByte[4:5])
        macPayload.fhdr = decodeFHDR(macPayloadByte[0:7 + fCtrl.fOptsLen])
        macPayload.fPort = macPayloadByte[7 + fCtrl.fOptsLen]

        frmPayload = FRMPayload()
        frmPayload.frames.append(Frame(base64.b64encode(macPayloadByte[7 + macPayload.fhdr.fCtrl.fOptsLen + 1:])))
        macPayload.frmPayload = frmPayload

        phyPayload.macPayload = macPayload
        phyPayload.mic = mic.hex()

        if mtype == MTYPE_UNCONFIRMED_DATA_UP:
            phyPayload.mhdr.mType = "UnconfirmedDataUp"
            print(" *** Unconfirmed data up")
        elif mtype == MTYPE_CONFIRMED_DATA_UP:
            print(" *** Confirmed data up")
            phyPayload.mhdr.mType = "ConfirmedDataUp"
        elif mtype == MTYPE_UNCONFIRMED_DATA_DOWN:
            phyPayload.mhdr.mType = "UnconfirmedDataDown"
            print(" *** Unconfirmed data down")
        else:
            print(" *** Confirmed data down")
            phyPayload.mhdr.mType = "ConfirmedDataDown"

        print("  DevAddr: %08s  " % phyPayload.macPayload.fhdr.devAddr)
        print("  fCtrl: %02s" % phyPayload.macPayload.fhdr.fCtrl.getString())
        print("  fCnt: %05d   fPort: %01x" % (phyPayload.macPayload.fhdr.fCnt, phyPayload.macPayload.fPort))
        print("  FRMPayload: %04s " % phyPayload.macPayload.frmPayload.frames[0].bytes)
        print("  mic: %04s " % phyPayload.mic)
    else:
        print("Unsupported type")

    return phyPayload


def get_mhdr(mhdr):
    if mhdr.major != "LoRaWANR1":
        raise Exception("Lorawan version must be 1.0 or 1.1")

    if mhdr.mType == "JoinRequest":
        return MTYPE_JOIN_REQUEST
    elif mhdr.mType == "JoinAccept":
        return MTYPE_JOIN_ACCEPT
    elif mhdr.mType == "UnconfirmedDataUp":
        return MTYPE_UNCONFIRMED_DATA_UP
    elif mhdr.mType == "ConfirmedDataUp":
        return MTYPE_CONFIRMED_DATA_UP
    elif mhdr.mType == "UnconfirmedDataDown":
        return MTYPE_UNCONFIRMED_DATA_DOWN
    elif mhdr.mType == "ConfirmedDataDown":
        return MTYPE_CONFIRMED_DATA_DOWN
    else:
        raise Exception("Invalid mType")


def encodeDevAddr(data):
    return data[::+1]


def encodeFHDR(fhdr):
    byte = bytearray()
    byte += encodeDevAddr(int(fhdr.devAddr, 16).to_bytes(4, 'little'))
    byte += fhdr.fCtrl.getByte()
    byte += fhdr.fCnt.to_bytes(2, 'big')
    return byte


def encodePhyPayload(phyPayload):
    mtype = get_mhdr(phyPayload.mhdr)
    data = bytearray()

    if mtype == MTYPE_JOIN_REQUEST:
        print(" *** Join-request")
        joinEUI = int(phyPayload.macPayload.joinEUI, 16).to_bytes(8, 'big')
        devEUI = int(phyPayload.macPayload.devEUI, 16).to_bytes(8, 'big')
        nonce = phyPayload.macPayload.devNonce.to_bytes(2, 'big')

        data += (mtype << 5).to_bytes(1, 'big')
        joinEUI = joinEUI[::-1]
        devEUI = devEUI[::-1]
        nonce = nonce[::-1]
        data += joinEUI
        data += devEUI
        data += nonce
        data += int(phyPayload.mic, 16).to_bytes(4, 'big')
        return base64.b64encode(data).decode()
    elif mtype == MTYPE_JOIN_ACCEPT:
        print(" *** Join Accept")
        data += (mtype << 5).to_bytes(1, 'big')
        data += base64.b64decode(phyPayload.macPayload.bytes.encode())
        data += int(phyPayload.mic, 16).to_bytes(4, 'big')
        return base64.b64encode(data).decode()
    elif mtype == MTYPE_CONFIRMED_DATA_UP or mtype == MTYPE_UNCONFIRMED_DATA_UP or mtype == MTYPE_CONFIRMED_DATA_DOWN or mtype == MTYPE_UNCONFIRMED_DATA_DOWN:

        data += (mtype << 5).to_bytes(1, 'big')

        data += encodeFHDR(phyPayload.macPayload.fhdr)
        data += int(phyPayload.macPayload.fPort).to_bytes(1, 'big')

        frmPayload = phyPayload.macPayload.frmPayload
        for frame in frmPayload.frames:
            data += base64.b64decode(frame.bytes)

        data += int(phyPayload.mic, 16).to_bytes(4, 'big')

        if mtype == MTYPE_UNCONFIRMED_DATA_UP:
            print(" *** Unconfirmed data up")
        elif mtype == MTYPE_CONFIRMED_DATA_UP:
            print(" *** Confirmed data up")
        elif mtype == MTYPE_UNCONFIRMED_DATA_DOWN:
            print(" *** Unconfirmed data down")
        else:
            print(" *** Confirmed data down")

        return base64.b64encode(data).decode()
    else:
        print("Unsupported type")


class PhyPayloadFEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def encodePhyPayloadFromJson(json_packet):
    p = PhyPayload()
    p.mhdr.mType = json_packet['mhdr']['mType']
    p.mhdr.major = json_packet['mhdr']['major']
    p.macPayload.fhdr.devAddr = json_packet['macPayload']['fhdr']['devAddr']
    p.macPayload.fhdr.fCtrl.ADR = json_packet['macPayload']['fhdr']['fCtrl']['adr']
    p.macPayload.fhdr.fCtrl.ADRACKReq = json_packet['macPayload']['fhdr']['fCtrl']['adrAckReq']
    p.macPayload.fhdr.fCtrl.ACK = json_packet['macPayload']['fhdr']['fCtrl']['ack']
    p.macPayload.fhdr.fCtrl.FPending = json_packet['macPayload']['fhdr']['fCtrl']['fPending']
    p.macPayload.fhdr.fCtrl.ClassB = json_packet['macPayload']['fhdr']['fCtrl']['classB']
    p.macPayload.fhdr.fCnt = json_packet['macPayload']['fhdr']['fCnt']
    p.macPayload.fPort = json_packet['macPayload']['fPort']
    for bytes_data in json_packet['macPayload']['frmPayload']:
        p.macPayload.frmPayload.frames.append(Frame(bytes_data['bytes']))
    p.mic = json_packet['mic']
    return encodePhyPayload(p)
