import base64
import json
import random

from enums.bcolors import BColors
from enums.lorawan_version_enum import LorawanVersionEnum
from enums.mac_command_enum import MacCommandEnum
from enums.major_type_enum import MajorTypeEnum
from enums.message_type_enum import MessageTypeEnum
from payloads.info.tx_info import TxInfo
from payloads.mac_layer.mac_command_payload import MacCommandItem, MacCommandPayload
from payloads.mac_layer.phy_payload import PhyPayload, MacPayload, FHDR, Frame
from payloads.mac_layer.watchdog_data import WatchdogData
from utils.coder import encode_phy_payload, decode_join_accept_mac_payload, encode_mac_commands_to_frm_payload, \
    encode_dev_addr
from utils.downlink_message_manager import manage_received_message
from utils.payload_util import compute_join_request_mic, compute_data_mic, encrypt_frm_payload


class Tags:
    def __init__(self, ok="value"):
        self.ok = ok

    def __eq__(self, other):
        if not isinstance(other, Tags):
            return NotImplemented
        return self.ok.__eq__(other.ok)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)


class Watchdog:
    def __init__(self, application_id="", application_name="", device_name="", dev_eui="", margin=None,
                 external_power_source=False, battery_level_unavailable=True, battery_level=255, tags=Tags(),
                 device_profile_id="", device_profile_name="", app_key="", net_skey="", app_skey="",
                 join_eui="0000000000000000", dev_addr=None, tx_info=TxInfo()):
        self.applicationID = application_id
        self.applicationName = application_name
        self.deviceName = device_name
        self.devEUI = dev_eui
        self.margin = margin
        self.externalPowerSource = external_power_source
        self.batteryLevelUnavailable = battery_level_unavailable
        self.batteryLevel = battery_level
        self.tags = tags
        self.deviceProfileID = device_profile_id
        self.deviceProfileName = device_profile_name
        self.app_key = app_key
        self.net_skey = net_skey
        self.app_skey = app_skey
        self.joinEUI = join_eui
        self.app_nonce = None
        self.net_ID = None
        self.dev_nonce = None
        self.gateways = []
        self.active = False
        self.dev_addr = dev_addr
        self.fCntUp = 0  # da incrementare ad ogni invio
        self.fCntDown = 0  # da incrementare ogni ricezione
        self.data = []
        self.timetosend = 5000  # timetosend ms
        self.timetoreceive = 5000  # timetoreceive in ms
        self.txInfo = tx_info

    def join(self):
        phy_payload = PhyPayload()
        phy_payload.mhdr.mType = MessageTypeEnum.JOIN_REQUEST.get_name()
        phy_payload.mhdr.major = MajorTypeEnum.LoRaWANR1.get_name()
        phy_payload.macPayload.devEUI = self.devEUI
        phy_payload.macPayload.joinEUI = self.joinEUI
        self.dev_nonce = random.randint(10000, 30000)
        phy_payload.macPayload.devNonce = self.dev_nonce
        phy_payload.mic = "0"
        phy_payload_encoded = base64.b64decode(encode_phy_payload(phy_payload))
        phy_payload.mic = compute_join_request_mic(phy_payload_encoded, self.app_key)
        phy_payload_encoded = encode_phy_payload(phy_payload)
        self.send(phy_payload_encoded)
        self.fCntUp += 1

    def send_data(self):
        if not self.active:
            return
        w_data = WatchdogData()
        w_data.battery = self.batteryLevel
        w_data.humidity = round(random.gauss(70, 20), 2)
        w_data.temperature = round(random.gauss(5, 6), 2)
        frame_payload = bytearray(base64.b64decode(w_data.encode_data()))

        dev_addr_byte = encode_dev_addr(int(self.dev_addr, 16).to_bytes(4, 'little'))
        ecrypted_frame_payload = encrypt_frm_payload(self.app_skey, self.net_skey, 1, True, dev_addr_byte, self.fCntUp,
                                                     frame_payload)
        ecrypted_frame_payload_encoded = base64.b64encode(ecrypted_frame_payload).decode()
        phy_payload = PhyPayload()
        # set MHDR
        phy_payload.mhdr.mType = MessageTypeEnum.UNCONFIRMED_DATA_UP.get_name()
        phy_payload.mhdr.major = MajorTypeEnum.LoRaWANR1.get_name()
        # set MacPayload
        mac_paylaod = MacPayload()
        # set FHDR
        fhdr = FHDR()
        fhdr.devAddr = self.dev_addr
        fhdr.fCnt = self.fCntUp

        fhdr.fCtrl.adr = True

        mac_paylaod.fhdr = fhdr
        mac_paylaod.fPort = 1
        mac_paylaod.frmPayload.append(Frame(ecrypted_frame_payload_encoded))

        phy_payload.macPayload = mac_paylaod
        phy_payload.mic = "0"
        phy_payload_encoded = base64.b64decode(encode_phy_payload(phy_payload))
        phy_payload.mic = compute_data_mic(phy_payload_encoded, LorawanVersionEnum.LoRaWANR1_0.value, self.fCntUp, 0, 0,
                                           self.net_skey, True)
        phy_payload_encoded = encode_phy_payload(phy_payload)
        self.fCntUp += 1
        self.data.append(w_data)
        if self.send(phy_payload_encoded):
            print(f"{BColors.HEADER.value}SUCCESS SEND DATA WATCHDOG: {self.deviceName}{BColors.ENDC.value}")
        else:
            print(f"{BColors.FAIL.value}FAILED SEND DATA WATCHDOG: {self.deviceName}{BColors.ENDC.value}")


    def __eq__(self, other):
        if not isinstance(other, Watchdog):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.applicationID.__eq__(other.applicationID) and self.applicationName.__eq__(other.applicationName) and \
               self.applicationName.__eq__(other.applicationName) and \
               self.deviceName.__eq__(other.deviceName) and self.devEUI.__eq__(other.devEUI) and \
               self.margin.__eq__(other.margin) and self.externalPowerSource.__eq__(other.externalPowerSource) and \
               self.batteryLevelUnavailable.__eq__(other.batteryLevelUnavailable) and \
               self.batteryLevel.__eq__(other.batteryLevel) and self.tags.__eq__(other.tags) and \
               self.active.__eq__(other.active)

    def activate(self, phy_payload):
        join_accept_mac_payload = decode_join_accept_mac_payload(self.app_key, self.dev_nonce, phy_payload)
        self.net_skey = join_accept_mac_payload.nwk_SKey
        self.app_skey = join_accept_mac_payload.app_SKey
        self.app_nonce = join_accept_mac_payload.app_nonce
        self.net_ID = join_accept_mac_payload.net_ID
        self.dev_addr = join_accept_mac_payload.dev_addr
        self.batteryLevelUnavailable = False
        self.batteryLevel = 254
        self.margin = 7
        self.active = True
        print(f"{BColors.HEADER.value}ACTIVATE WATCHDOG: {self.deviceName}{BColors.ENDC.value}")

    def receive_message(self, phy_payload, tx_info):
        result = manage_received_message(self, phy_payload)
        self.txInfo = tx_info
        self.fCntDown += 1
        return result

    def send_device_status(self):
        if not self.active:
            return

        mac_command = MacCommandItem()
        mac_command_payload = MacCommandPayload()
        mac_command_payload.margin = self.margin
        mac_command_payload.battery = self.batteryLevel
        mac_command.payload = mac_command_payload
        mac_command.cid = MacCommandEnum.DEVICE_STATUS_ANS.get_name()
        frm_payload_encoded = encode_mac_commands_to_frm_payload(self.app_skey,
                                                                 self.net_skey, 0,
                                                                 True, self.dev_addr, self.fCntUp, [mac_command])
        # setting phy payload
        phy_payload = PhyPayload()
        phy_payload.mhdr.mType = MessageTypeEnum.UNCONFIRMED_DATA_UP.get_name()
        phy_payload.mhdr.major = MajorTypeEnum.LoRaWANR1.get_name()
        # setting mac payload
        mac_payload = MacPayload()
        mac_payload.fPort = 0
        mac_payload.frmPayload.append(Frame(frm_payload_encoded))
        # setting fhdr payload
        fhdr = FHDR()
        fhdr.devAddr = self.dev_addr
        fhdr.fCnt = self.fCntUp
        fhdr.fCtrl.adr = True

        mac_payload.fhdr = fhdr

        phy_payload.macPayload = mac_payload
        phy_payload.mic = "0"
        phy_payload_encoded = base64.b64decode(encode_phy_payload(phy_payload))
        phy_payload.mic = compute_data_mic(phy_payload_encoded, LorawanVersionEnum.LoRaWANR1_0.value, self.fCntUp, 0, 0,
                                           self.net_skey, True)
        phy_payload_encoded = encode_phy_payload(phy_payload)
        self.fCntUp += 1
        if self.send(phy_payload_encoded):
            print(f"{BColors.HEADER.value}SUCCESS SEND STATUS WATCHDOG: {self.deviceName}{BColors.ENDC.value}")
        else:
            print(f"{BColors.FAIL.value}FAILED SEND STATUS WATCHDOG: {self.deviceName}{BColors.ENDC.value}")

    def send(self, phy_payload):
        result = False
        for gateway in self.gateways:
            result = result or gateway.up_link_publish(phy_payload)
        return result
    def configure(self, downlink_configuration_payload):
        self.timetosend = downlink_configuration_payload.timetosend
        self.timetoreceive = downlink_configuration_payload.timetoreceive
        print(f"{BColors.HEADER.value}CONFIGURED WATCHDOG: {self.deviceName} - "
              f"timetosend:{self.timetosend}ms timetoreceive:{self.timetoreceive}ms{BColors.ENDC.value}")

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)
