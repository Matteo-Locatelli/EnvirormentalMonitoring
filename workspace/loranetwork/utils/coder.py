import base64
import struct

from enums.mac_command_enum import MacCommandEnum
from enums.major_type_enum import MajorTypeEnum
from payloads.mac_layer.mac_payload import MacCommandItem, MacCommandPayload
from payloads.mac_layer.phy_payload import *
from enums.message_type_enum import MessageTypeEnum
from utils.payload_util import encrypt_frm_payload


def MType(byte):
    return struct.unpack("B", byte)[0] >> 5


def Major(byte):
    return struct.unpack("B", byte)[0] & 0x03


def decodeDevAddr(data):
    return data[::-1]


def decodeMic(data):
    return data[::-1]


def decodeFHDR(data):
    fhdr = FHDR()
    fhdr.devAddr = decodeDevAddr(data[0:4]).hex()
    fhdr.fCtrl = FCTRL(data[4:5])
    fCnt_byte = data[5:7]
    fCnt_byte += bytearray(2)
    fhdr.fCnt = int.from_bytes(fCnt_byte, 'little')
    if len(data) > 7:
        fhdr.fOpts.append(Frame(base64.b64encode(data[7:])))
    return fhdr


def get_command_payload(command_type, data):
    mac_command_payload = MacCommandPayload()
    if command_type == MacCommandEnum.DEVICE_STATUS_ANS:
        mac_command_payload.battery = data[0]
        if data[1] > 31:
            mac_command_payload.margin = data[1] - 64
        else:
            mac_command_payload.margin = data[1]
    elif command_type == MacCommandEnum.NEW_CHANNEL_REQ:
        mac_command_payload.chIndex = data[0]
        mac_command_payload.freq = int.from_bytes(data[1:4], 'little') * 100
        mac_command_payload.maxDR = data[4] & ((1 << 3) ^ (1 << 2) ^ (1 << 1) ^ (1 << 0))
        mac_command_payload.minDR = (data[4] & ((1 << 7) ^ (1 << 6) ^ (1 << 5) ^ (1 << 4))) >> 4

    return mac_command_payload


def decode_data_payload_to_mac_commands(is_uplink, frames):
    if len(frames) == 0:
        return []

    if len(frames) != 1:
        raise Exception("lorawan: exactly one Payload expected")

    data = frames[0]

    mac_command_payload_list = []
    i = 0
    while i < len(data):
        mac_command_payload = MacCommandItem()
        command_type = MacCommandEnum.findByKey(data[i], is_uplink)
        if command_type is None:
            raise Exception("Unknown mac command")
        payloadLenght = command_type.getPayloadLenght()
        mac_command_payload.cid = command_type.getName()
        mac_command_payload.payload = get_command_payload(command_type, data[i + 1:i + 1 + payloadLenght])
        mac_command_payload_list.append(mac_command_payload)
        i = i + 1 + payloadLenght

    return mac_command_payload_list


def decode_fopts_payload_to_mac_commands(is_uplink, frames):
    data = []
    if frames is None:
        return data
    for frame in frames:
        data.append(base64.b64decode(frame.bytes))
    return decode_data_payload_to_mac_commands(is_uplink, data)


def decode_frm_payload_to_mac_commands(app_key, is_uplink, dev_addr, fCnt, frames):
    data = []
    for frame in frames:
        data.append(bytearray(base64.b64decode(frame.bytes)))

    dev_addr_byte = encodeDevAddr(int(dev_addr, 16).to_bytes(4, 'big'))
    encrypted_data = []
    for d in data:
        encrypted_data.append(encrypt_frm_payload(app_key, is_uplink, dev_addr_byte, fCnt, d))

    return decode_data_payload_to_mac_commands(is_uplink, encrypted_data)


def decodePhyPayload(phy_payload_encoded):
    data = base64.b64decode(phy_payload_encoded)

    phyPayload = PhyPayload()
    mhdrByte = data[0].to_bytes(1, 'big')
    macPayloadByte = data[1:-4]
    mic = data[-4:]
    assert (len(data) == len(mhdrByte) + len(macPayloadByte) + len(mic))

    mtype_key = MType(mhdrByte)
    major_key = Major(mhdrByte)
    mtype = MessageTypeEnum.findByKey(mtype_key)
    major = MajorTypeEnum.findByKey(major_key)

    phyPayload.mhdr = MHDR()

    if major != MajorTypeEnum.LoRaWANR1:
        raise Exception("Lorawan version must be 1.0 or 1.1")
    else:
        phyPayload.mhdr.major = major.getName()

    if mtype == MessageTypeEnum.JOIN_REQUEST:
        print(" *** Join-request")
        joinEUI = data[1:9]
        devEUI = data[9:17]
        nonce = data[17:19]

        phyPayload.macPayload = MacPayload()
        joinEUI = joinEUI[::-1]
        devEUI = devEUI[::-1]
        nonce = nonce[::-1]
        phyPayload.mhdr.mType = mtype.getName()
        phyPayload.macPayload.joinEUI = joinEUI.hex()
        phyPayload.macPayload.devEUI = devEUI.hex()
        phyPayload.macPayload.devNonce = int.from_bytes(nonce, 'big')
        phyPayload.mic = mic.hex()
        print("  JoinEUI: %s" % joinEUI.hex())
        print("  DevEUI: %s" % devEUI.hex())
        print("  Nonce:  %s" % nonce.hex())
        print("  MIC: %s" % mic.hex())
    elif mtype == MessageTypeEnum.JOIN_ACCEPT:
        print(" *** Join Accept")
        phyPayload.mhdr.mType = mtype.getName()
        phyPayload.macPayload = MacPayload()
        phyPayload.macPayload.bytes = base64.b64encode(macPayloadByte).decode()
        phyPayload.mic = mic.hex()
        print("  Data base64 encoded: %s" % base64.b64encode(macPayloadByte))
    elif mtype == MessageTypeEnum.UNCONFIRMED_DATA_UP or mtype == MessageTypeEnum.CONFIRMED_DATA_UP \
            or mtype == MessageTypeEnum.UNCONFIRMED_DATA_UP or mtype == MessageTypeEnum.UNCONFIRMED_DATA_DOWN:
        phyPayload.mhdr.mType = mtype.getName()
        macPayload = MacPayload()

        fCtrl = FCTRL(macPayloadByte[4:5])
        macPayload.fhdr = decodeFHDR(macPayloadByte[0:7 + fCtrl.fOptsLen])
        macPayload.fPort = macPayloadByte[7 + fCtrl.fOptsLen]
        if len(macPayloadByte[7 + macPayload.fhdr.fCtrl.fOptsLen + 1:]) > 0:
            macPayload.frmPayload.append(Frame(base64.b64encode(macPayloadByte[7 + macPayload.fhdr.fCtrl.fOptsLen + 1:])))

        phyPayload.macPayload = macPayload
        phyPayload.mic = mic.hex()

        print(" *** ", mtype.getName())

        print("  DevAddr: %08s  " % phyPayload.macPayload.fhdr.devAddr)
        print("  fCtrl: %02s" % phyPayload.macPayload.fhdr.fCtrl.getString())
        print("  fCnt: %05d   fPort: %01x" % (phyPayload.macPayload.fhdr.fCnt, phyPayload.macPayload.fPort))
        if len(phyPayload.macPayload.frmPayload) > 0:
            print("  FRMPayload: %04s " % phyPayload.macPayload.frmPayload[0].bytes)
        print("  mic: %04s " % phyPayload.mic)
    else:
        print("Unsupported type")

    return phyPayload


def encodeDevAddr(data):
    return data[::+1]


def encodeFHDR(fhdr):
    byte = bytearray()
    byte += encodeDevAddr(int(fhdr.devAddr, 16).to_bytes(4, 'little'))
    byte += fhdr.fCtrl.getByte()
    byte += fhdr.fCnt.to_bytes(2, 'little')
    return byte


def encodePhyPayload(phyPayload):
    print("encodePhyPayload")
    mtype = MessageTypeEnum.findByName(phyPayload.mhdr.mType)
    data = bytearray()
    print(" *** encoding", mtype.getName())

    if mtype == MessageTypeEnum.JOIN_REQUEST:
        joinEUI = int(phyPayload.macPayload.joinEUI, 16).to_bytes(8, 'big')
        devEUI = int(phyPayload.macPayload.devEUI, 16).to_bytes(8, 'big')
        nonce = phyPayload.macPayload.devNonce.to_bytes(2, 'big')

        data += (mtype.getKey() << 5).to_bytes(1, 'big')
        joinEUI = joinEUI[::-1]
        devEUI = devEUI[::-1]
        nonce = nonce[::-1]
        data += joinEUI
        data += devEUI
        data += nonce
        data += int(phyPayload.mic, 16).to_bytes(4, 'big')
        return base64.b64encode(data).decode()
    elif mtype == MessageTypeEnum.JOIN_ACCEPT:
        data += (mtype.getKey() << 5).to_bytes(1, 'big')
        data += base64.b64decode(phyPayload.macPayload.bytes.encode())
        data += int(phyPayload.mic, 16).to_bytes(4, 'big')
        return base64.b64encode(data).decode()
    elif mtype == MessageTypeEnum.CONFIRMED_DATA_UP or mtype == MessageTypeEnum.UNCONFIRMED_DATA_UP \
            or mtype == MessageTypeEnum.CONFIRMED_DATA_UP or mtype == MessageTypeEnum.UNCONFIRMED_DATA_DOWN:

        data += (mtype.getKey() << 5).to_bytes(1, 'big')

        data += encodeFHDR(phyPayload.macPayload.fhdr)
        data += int(phyPayload.macPayload.fPort).to_bytes(1, 'big')

        frmPayload = phyPayload.macPayload.frmPayload
        for frame in frmPayload:
            data += base64.b64decode(frame.bytes)

        data += int(phyPayload.mic, 16).to_bytes(4, 'big')

        return base64.b64encode(data).decode()
    else:
        print("Unsupported type")


def encodePhyPayloadFromJson(json_packet):
    return encodePhyPayload(getPhyPayloadFromJson(json_packet))


def getPhyPayloadFromJson(json_packet):
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
    if json_packet['macPayload']['frmPayload'] is not None:
        for bytes_data in json_packet['macPayload']['frmPayload']:
            p.macPayload.frmPayload.append(Frame(bytes_data['bytes']))
    p.mic = json_packet['mic']
    return p
