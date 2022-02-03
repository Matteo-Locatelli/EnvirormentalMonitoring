import base64

from enums.lorawan_version_enum import LorawanVersionEnum
from enums.mac_command_enum import MacCommandEnum
from enums.message_type_enum import MessageTypeEnum
from utils.coder import decodePhyPayload, decode_frm_payload_to_mac_commands
from utils.payload_util import compute_join_accept_mic, compute_data_mic, getJsonFromObject


def manage_received_message(watchdog, phyPayloadEncoded):
    phyPayload = decodePhyPayload(phyPayloadEncoded)
    print("Watchdog received message: ", getJsonFromObject(phyPayload))
    if phyPayload.macPayload.fhdr.devAddr != watchdog.dev_addr:
        return False

    if phyPayload.mhdr.mType == MessageTypeEnum.JOIN_ACCEPT.getName():
        mic = compute_join_accept_mic(base64.b64decode(phyPayloadEncoded), watchdog.app_key)
    elif phyPayload.mhdr.mType == MessageTypeEnum.UNCONFIRMED_DATA_DOWN.getName() or \
            phyPayload.mhdr.mType == MessageTypeEnum.CONFIRMED_DATA_DOWN.getName():
        mic = compute_data_mic(base64.b64decode(phyPayloadEncoded), LorawanVersionEnum.LoRaWANR1_0.value,
                               watchdog.fCntDown, 0, 0, watchdog.net_skey, False)
    else:
        print("Unknown downlink message")
        return False

    if mic != phyPayload.mic:
        print("Invalid MIC ")
        return False

    if phyPayload.mhdr.mType == MessageTypeEnum.JOIN_ACCEPT.getName():
        watchdog.activate(phyPayload)
        return True
    if phyPayload.mhdr.mType == MessageTypeEnum.UNCONFIRMED_DATA_DOWN.getName() or \
            phyPayload.mhdr.mType == MessageTypeEnum.CONFIRMED_DATA_DOWN.getName():
        if phyPayload.macPayload.fPort == 0:
            manage_mac_commands(watchdog, phyPayload)
        return True
    return False


def manage_mac_commands(watchdog, phyPayload):
    message_type = MessageTypeEnum.findByName(phyPayload.mhdr.mType)
    mac_command_list = decode_frm_payload_to_mac_commands(watchdog.app_skey, watchdog.net_skey,
                                                          phyPayload.macPayload.fPort,
                                                          message_type.isUplink(),
                                                          phyPayload.macPayload.fhdr.devAddr,
                                                          phyPayload.macPayload.fhdr.fCnt,
                                                          phyPayload.macPayload.frmPayload)

    for mac_command in mac_command_list:
        if mac_command.cid == MacCommandEnum.DEVICE_STATUS_REQ.getName():
            watchdog.send_device_status()
