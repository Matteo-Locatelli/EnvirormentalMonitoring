from enums.mac_command_enum import MacCommandEnum
from enums.message_type_enum import MessageTypeEnum
from utils.coder import decodePhyPayload, decode_join_accept_mac_payload, decode_frm_payload_to_mac_commands
from utils.payload_util import compute_join_request_mic, compute_join_accept_mic, compute_data_mic


def manage_received_message(self, watchdog, phyPayloadEncoded):
    phyPayloadEncoded = decodePhyPayload(phyPayloadEncoded)
    if phyPayloadEncoded.macPayload.fhdr.devAddr != watchdog.dev:
        return False

    mic = None
    if phyPayloadEncoded.mhdr.mType == MessageTypeEnum.JOIN_ACCEPT.getName():
        mic = compute_join_accept_mic(phyPayloadEncoded, watchdog.app_key)
    elif phyPayloadEncoded.mhdr.mType == MessageTypeEnum.UNCONFIRMED_DATA_DOWN.getName() or \
            phyPayloadEncoded.mhdr.mType == MessageTypeEnum.CONFIRMED_DATA_DOWN.getName():
        mic = compute_data_mic(phyPayloadEncoded, watchdog.app_key)
    else:
        print("Unknown downlink message")
        return False
    if mic != phyPayloadEncoded.mic:
        print("Invalid MIC ")
        return False

    if phyPayloadEncoded.mhdr.mType == MessageTypeEnum.JOIN_ACCEPT.getName():
        watchdog.activate(phyPayloadEncoded)
        return True
    elif phyPayloadEncoded.mhdr.mType == MessageTypeEnum.UNCONFIRMED_DATA_DOWN.getName() or \
            phyPayloadEncoded.mhdr.mType == MessageTypeEnum.CONFIRMED_DATA_DOWN.getName():
        manage_mac_commands(watchdog, phyPayloadEncoded)
        return True


def manage_mac_commands(watchdog, phyPayloadEncoded):
    message_type = MessageTypeEnum.findByName(phyPayloadEncoded.mhdr.mType)
    mac_command_list = decode_frm_payload_to_mac_commands(watchdog.app_key, message_type.isUplink(),
                                                          phyPayloadEncoded.macPayload.fhdr.devAddr,
                                                          phyPayloadEncoded.macPayload.fhdr.fCnt,
                                                          phyPayloadEncoded.macPayload.frmPayload)

    for mac_command in mac_command_list:
        if mac_command.cid == MacCommandEnum.DEVICE_STATUS_REQ.getName():
            watchdog.send_device_status()
