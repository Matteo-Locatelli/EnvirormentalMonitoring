import base64
import json

from enums.bcolors import BColors
from enums.lorawan_version_enum import LorawanVersionEnum
from enums.mac_command_enum import MacCommandEnum
from enums.message_type_enum import MessageTypeEnum
from payloads.mac_layer.downlink_configuration_payload import DownlinkConfigurationPayload
from utils.coder import decodePhyPayload, decode_frm_payload_to_mac_commands, encodeDevAddr, \
    decode_fopts_payload_to_mac_commands
from utils.payload_util import compute_join_accept_mic, compute_data_mic, getJsonFromObject, encrypt_frm_payload


def manage_received_message(watchdog, phyPayloadEncoded):
    phyPayload = decodePhyPayload(phyPayloadEncoded)
    print(f"{BColors.HEADER.value}WATCHDOG {watchdog.deviceName} RECEIVED {phyPayload.mhdr.mType}{BColors.ENDC.value}")
    if phyPayload.macPayload.fhdr.devAddr != watchdog.dev_addr:
        return False

    if phyPayload.mhdr.mType == MessageTypeEnum.JOIN_ACCEPT.getName():
        mic = compute_join_accept_mic(base64.b64decode(phyPayloadEncoded), watchdog.app_key)
    elif phyPayload.mhdr.mType == MessageTypeEnum.UNCONFIRMED_DATA_DOWN.getName() or \
            phyPayload.mhdr.mType == MessageTypeEnum.CONFIRMED_DATA_DOWN.getName():
        mic = compute_data_mic(base64.b64decode(phyPayloadEncoded), LorawanVersionEnum.LoRaWANR1_0.value,
                               watchdog.fCntDown, 0, 0, watchdog.net_skey, False)
    else:
        print(f"{BColors.WARNING.value}Unknown downlink message{BColors.ENDC.value}")
        return False

    if mic != phyPayload.mic:
        print(f"{BColors.WARNING.value}Invalid MIC {BColors.ENDC.value}")
        return False

    if phyPayload.mhdr.mType == MessageTypeEnum.JOIN_ACCEPT.getName():
        watchdog.activate(phyPayload)
        return True
    if phyPayload.mhdr.mType == MessageTypeEnum.UNCONFIRMED_DATA_DOWN.getName() or \
            phyPayload.mhdr.mType == MessageTypeEnum.CONFIRMED_DATA_DOWN.getName():
        manage_mac_commands(watchdog, phyPayload)
        if phyPayload.macPayload.fPort is not None and phyPayload.macPayload.fPort > 0:
            manage_configuration_message(watchdog, phyPayload)
        return True
    return False


def manage_mac_commands(watchdog, phyPayload):
    message_type = MessageTypeEnum.findByName(phyPayload.mhdr.mType)
    mac_command_list = []
    mac_command_list.extend(decode_fopts_payload_to_mac_commands(message_type.isUplink(),
                                                                 phyPayload.macPayload.fhdr.fOpts))
    mac_command_list.extend(decode_frm_payload_to_mac_commands(watchdog.app_skey, watchdog.net_skey,
                                                               phyPayload.macPayload.fPort,
                                                               message_type.isUplink(),
                                                               phyPayload.macPayload.fhdr.devAddr,
                                                               phyPayload.macPayload.fhdr.fCnt,
                                                               phyPayload.macPayload.frmPayload))
    for mac_command in mac_command_list:
        if mac_command.cid == MacCommandEnum.DEVICE_STATUS_REQ.getName():
            watchdog.send_device_status()


def manage_configuration_message(watchdog, phyPayload):
    if phyPayload.macPayload.frmPayload is None or len(phyPayload.macPayload.frmPayload) <= 0:
        return
    encrypted_frm_payload = bytearray(base64.b64decode(phyPayload.macPayload.frmPayload[0].bytes))
    dev_addr_byte = encodeDevAddr(int(phyPayload.macPayload.fhdr.devAddr, 16).to_bytes(4, 'little'))
    decrypted_frm_payload = encrypt_frm_payload(watchdog.app_skey, watchdog.net_skey,
                                                phyPayload.macPayload.fPort,
                                                False,
                                                dev_addr_byte,
                                                phyPayload.macPayload.fhdr.fCnt,
                                                encrypted_frm_payload)
    downlink_configuration_payload = DownlinkConfigurationPayload()
    json_frm_payload = json.loads(decrypted_frm_payload.decode())
    downlink_configuration_payload.timetosend = json_frm_payload['timetosend']
    downlink_configuration_payload.timetoreceive = json_frm_payload['timetoreceive']
    watchdog.configure(downlink_configuration_payload)
