import base64
import json

from enums.bcolors import BColors
from enums.lorawan_version_enum import LorawanVersionEnum
from enums.mac_command_enum import MacCommandEnum
from enums.message_type_enum import MessageTypeEnum
from payloads.mac_layer.downlink_configuration_payload import DownlinkConfigurationPayload
from utils.coder import decode_phy_payload, decode_frm_payload_to_mac_commands, encode_dev_addr, \
    decode_fopts_payload_to_mac_commands
from utils.payload_util import compute_join_accept_mic, compute_data_mic, encrypt_frm_payload


def manage_received_message(watchdog, phy_payload_encoded):
    phy_payload = decode_phy_payload(phy_payload_encoded)
    print(f"{BColors.HEADER.value}WATCHDOG {watchdog.deviceName} RECEIVED {phy_payload.mhdr.mType}{BColors.ENDC.value}")
    if phy_payload.macPayload.fhdr.devAddr != watchdog.dev_addr:
        return False

    if phy_payload.mhdr.mType == MessageTypeEnum.JOIN_ACCEPT.get_name():
        mic = compute_join_accept_mic(base64.b64decode(phy_payload_encoded), watchdog.app_key)
    elif phy_payload.mhdr.mType == MessageTypeEnum.UNCONFIRMED_DATA_DOWN.get_name() or \
            phy_payload.mhdr.mType == MessageTypeEnum.CONFIRMED_DATA_DOWN.get_name():
        mic = compute_data_mic(base64.b64decode(phy_payload_encoded), LorawanVersionEnum.LoRaWANR1_0.value,
                               watchdog.fCntDown, 0, 0, watchdog.net_skey, False)
    else:
        print(f"{BColors.WARNING.value}Unknown downlink message{BColors.ENDC.value}")
        return False

    if mic != phy_payload.mic:
        print(f"{BColors.WARNING.value}Invalid MIC {BColors.ENDC.value}")
        return False

    if phy_payload.mhdr.mType == MessageTypeEnum.JOIN_ACCEPT.get_name():
        watchdog.activate(phy_payload)
        return True
    if phy_payload.mhdr.mType == MessageTypeEnum.UNCONFIRMED_DATA_DOWN.get_name() or \
            phy_payload.mhdr.mType == MessageTypeEnum.CONFIRMED_DATA_DOWN.get_name():
        manage_mac_commands(watchdog, phy_payload)
        if phy_payload.macPayload.fPort is not None and phy_payload.macPayload.fPort > 0:
            manage_configuration_message(watchdog, phy_payload)
        return True
    return False


def manage_mac_commands(watchdog, phy_payload):
    message_type = MessageTypeEnum.find_by_name(phy_payload.mhdr.mType)
    mac_command_list = []
    mac_command_list.extend(decode_fopts_payload_to_mac_commands(message_type.is_uplink(),
                                                                 phy_payload.macPayload.fhdr.fOpts))
    mac_command_list.extend(decode_frm_payload_to_mac_commands(watchdog.app_skey, watchdog.net_skey,
                                                               phy_payload.macPayload.fPort,
                                                               message_type.is_uplink(),
                                                               phy_payload.macPayload.fhdr.devAddr,
                                                               phy_payload.macPayload.fhdr.fCnt,
                                                               phy_payload.macPayload.frmPayload))
    for mac_command in mac_command_list:
        if mac_command.cid == MacCommandEnum.DEVICE_STATUS_REQ.get_name():
            watchdog.send_device_status()


def manage_configuration_message(watchdog, phy_payload):
    if phy_payload.macPayload.frmPayload is None or len(phy_payload.macPayload.frmPayload) <= 0:
        return
    if phy_payload.macPayload.fPort is not None and phy_payload.macPayload.fPort == 0:
        return
    encrypted_frm_payload = bytearray(base64.b64decode(phy_payload.macPayload.frmPayload[0].bytes))
    dev_addr_byte = encode_dev_addr(int(phy_payload.macPayload.fhdr.devAddr, 16).to_bytes(4, 'little'))
    decrypted_frm_payload = encrypt_frm_payload(watchdog.app_skey, watchdog.net_skey,
                                                phy_payload.macPayload.fPort,
                                                False,
                                                dev_addr_byte,
                                                phy_payload.macPayload.fhdr.fCnt,
                                                encrypted_frm_payload)
    downlink_configuration_payload = DownlinkConfigurationPayload()
    # json_frm_payload = json.loads(base64.b64decode(decrypted_frm_payload.decode()).decode())
    json_frm_payload = json.loads(decrypted_frm_payload.decode())
    downlink_configuration_payload.timetosend = json_frm_payload['timetosend']
    downlink_configuration_payload.timetoreceive = json_frm_payload['timetoreceive']
    watchdog.configure(downlink_configuration_payload)
