import json

from Crypto.Hash import CMAC
from Crypto.Cipher import AES
from typing import TypeVar

T = TypeVar('T')

LoRaWANR1_0 = "LoRaWANR1"


def encrypt_frm_payload(app_key, is_uplink, dev_addr_byte, fCnt, data):
    key = bytes.fromhex(app_key)
    #key = app_key
    pLen = len(data)
    if pLen % 16 != 0:
        data += bytearray(16 - (pLen % 16))

    cipher = AES.new(key, AES.MODE_ECB)

    s = bytearray(16)
    a = bytearray(16)
    a[0] = 0x01
    if not is_uplink:
        a[5] = 0x01

    a[6:10] = dev_addr_byte
    temp = bytearray(2)
    temp += fCnt.to_bytes(2, 'big')
    fCnt = int.from_bytes(temp, 'big')
    a[10:14] = fCnt.to_bytes(4, 'little')

    i = 0
    while i < len(data) / 16:
        a[15] = int(i + 1)
        s[:] = cipher.decrypt(a)
        j = 0
        while j < len(s):
            data[i * 16 + j] = data[i * 16 + j] ^ s[j]
            j += 1

        i += 1

    return data[0:pLen]


def compute_join_request_mic(phy_payload, app_key):
    key = bytes.fromhex(app_key)
    mic = bytearray(4)
    mhdr = phy_payload[0:1]
    mac_payload = phy_payload[1:-4]

    mic_bytes = bytearray()
    mic_bytes += mhdr
    mic_bytes += mac_payload

    ap_mic = CMAC.new(key, ciphermod=AES)
    ap_mic.update(mic_bytes)
    mic[:] = ap_mic.digest()[0:4]

    return mic.hex()


def compute_uplink_data_mic(phy_payload, mac_version, confFCnt, txDR, txCh, fNwkSIntKey):
    mic = bytearray(4)
    key = bytes.fromhex(fNwkSIntKey)
    sNwkSIntKey = bytearray(16)
    mhdr = phy_payload[0:1]
    mac_payload = phy_payload[1:-4]
    fhdr = mac_payload[0:7]

    # confFCnt set to 0when there are no ack
    if not (int.from_bytes(fhdr[4:5], 'big') & 0x20) != 0:
        confFCnt = 0

    confFCnt = confFCnt % (1 << 16)

    mic_bytes = bytearray()
    mic_bytes += mhdr
    mic_bytes += mac_payload

    b0 = bytearray(16)
    b1 = bytearray(16)

    b0[0] = 0x49
    b1[0] = 0x49

    fhdr = mac_payload[0:7]
    dev_adress_byte = fhdr[0:4]

    # devAddr
    b0[6:10] = dev_adress_byte
    b1[6:10] = dev_adress_byte

    # fcntup
    temp = bytearray(2)
    temp += fhdr[5:7]
    fCnt = int.from_bytes(temp, 'big')
    b0[10:14] = fCnt.to_bytes(4, 'little')
    b1[10:14] = fCnt.to_bytes(4, 'little')

    b0[15] = len(mic_bytes)
    b1[15] = len(mic_bytes)

    # set up remaining bytes
    b1[1:3] = confFCnt.to_bytes(2, 'little')
    b1[3] = txDR
    b1[4] = txCh

    fn_mic = CMAC.new(key, ciphermod=AES)
    fn_mic.update(mic_bytes)
    if mac_version == LoRaWANR1_0:
        mic[:] = fn_mic.digest()[0:4]

    return mic.hex()


def getJsonFromObject(obj: T):
    json_str_object = json.dumps(obj.toJson())
    json_object = json.loads(json_str_object)

    def remove_nulls(d):
        return {k: v for k, v in d.items() if v is not None}

    return json.loads(json_object, object_hook=remove_nulls)
