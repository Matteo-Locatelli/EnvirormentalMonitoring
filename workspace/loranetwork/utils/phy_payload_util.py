from Crypto.Hash import CMAC
from Crypto.Cipher import AES
import binascii
import os

LoRaWANR1_0 = "LoRaWANR1"


def compute_join_request_mic(phy_payload, app_key):
    key = bytes.fromhex(app_key)
    mic = bytearray(4)
    mhdr = phy_payload[0:1]
    mac_payload = phy_payload[1:-4]

    mic_bytes = bytearray()
    mic_bytes += mhdr
    mic_bytes += mac_payload

    IV = os.urandom(16)

    ap_mic = CMAC.new(key, ciphermod=AES)
    ap_mic.update(mic_bytes)
    mic[:] = ap_mic.digest()[0:4]

    return mic.hex()


def compute_uplink_data_mic(phy_payload, mac_version, confFCnt, txDR, txCh, fNwkSIntKey):
    mic = bytearray(4)
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

    sn_mic = CMAC.new(fNwkSIntKey.encode(), ciphermod=AES)

    if mac_version == LoRaWANR1_0:  # mic[:] = cmacF[0:4]
        mic[0:4] = sn_mic.digest()[0:4]

    return mic.hex()


def compute_mic(data, devAdress, netSessionKey):
    # based on https://lora-alliance.org/sites/default/files/2018-04/lorawantm_specification_-v1.1.pdf#page=27

    fcntup = [0x00, 0x00, 0x00, 0x00]

    b0 = [0x49, 0x00, 0x00, 0x00, 0x00]
    b0 += [0x00]  # dir
    b0 += devAdress[::-1]
    b0 += fcntup
    b0 += [0x00]
    b0 += [len(data)]
    b0 += data

    b1 = [0x49, 0x00, 0x00]
    b1 += [0x02]  # txdr
    b1 += [0x00]  # txch
    b1 += [0x00]  # dir
    b1 += devAdress[::-1]
    b1 += fcntup
    b1 += [0x00]
    b1 += [len(data)]
    b1 += data

    # sn_mic = CMAC.encode(bytes(netSessionKey), bytes(b1))[:2]
    sn_mic = CMAC.new(netSessionKey, ciphermod=AES)
    fn_mic = CMAC.encode(bytes("config['fnwksintkey']"), bytes(b0))[:2]
    mic = list(map(int, sn_mic))
    mic += list(map(int, fn_mic))
    return mic
