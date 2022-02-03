import json

from utils.downlink_message_manager import manage_received_message
from enums.lorawan_version_enum import LorawanVersionEnum
from enums.mac_command_enum import MacCommandEnum
from enums.major_type_enum import MajorTypeEnum
from enums.message_type_enum import MessageTypeEnum
from payloads.mac_layer.mac_command_payload import MacCommandItem, MacCommandPayload
from payloads.mac_layer.phy_payload import PhyPayload, MacPayload, FHDR, Frame
import random
import base64

from utils.coder import encodePhyPayload, decode_join_accept_mac_payload, encode_mac_commands_to_frm_payload, \
    encodeDevAddr
from utils.payload_util import compute_join_request_mic, getJsonFromObject, compute_data_mic, encrypt_frm_payload
from payloads.watchdog_data import WatchdogData


class Tags:
    def __init__(self, ok="value"):
        self.ok = ok

    def __eq__(self, other):
        if not isinstance(other, Tags):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.ok.__eq__(other.ok)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)


# def getRandomData():

class Watchdog:
    def __init__(self, applicationID="", applicationName="", deviceName="", devEUI="", margin=None,
                 externalPowerSource=False, batteryLevelUnavailable=True, batteryLevel=255, tags=Tags(),
                 deviceProfileID="", deviceProfileName="", app_key="", net_skey="", app_skey="",
                 joinEUI="0000000000000000"):
        self.applicationID = applicationID
        self.applicationName = applicationName
        self.deviceName = deviceName
        self.devEUI = devEUI
        self.margin = margin
        self.externalPowerSource = externalPowerSource
        self.batteryLevelUnavailable = batteryLevelUnavailable
        self.batteryLevel = batteryLevel
        self.tags = tags
        self.deviceProfileID = deviceProfileID
        self.deviceProfileName = deviceProfileName
        self.app_key = app_key
        self.net_skey = net_skey
        self.app_skey = app_skey
        self.joinEUI = joinEUI
        self.app_nonce = None
        self.net_ID = None
        self.dev_nonce = None
        self.gateway = None
        self.active = False
        self.dev_addr = None
        self.fCntUp = 0  # da incrementare ad ogni invio
        self.fCntDown = 0  # da incrementare ogni ricezione
        self.data = []
        self.timetosend = 10000  # timetosend ms
        self.timetoreceive = 40000  # timetoreceive in ms
        self.previousMillisS = 0
        self.previousMillisR = 0
        self.txInfo = None
        self.previousMillisBatteryUpdate = 0

    def join(self):
        phy_payload = PhyPayload()
        phy_payload.mhdr.mType = MessageTypeEnum.JOIN_REQUEST.getName()
        phy_payload.mhdr.major = MajorTypeEnum.LoRaWANR1.getName()
        phy_payload.macPayload.devEUI = self.devEUI
        phy_payload.macPayload.joinEUI = self.joinEUI
        self.dev_nonce = random.randint(10000, 30000)
        phy_payload.macPayload.devNonce = self.dev_nonce
        phy_payload.mic = "0"
        phy_payload_encoded = base64.b64decode(encodePhyPayload(phy_payload))
        phy_payload.mic = compute_join_request_mic(phy_payload_encoded, self.app_key)
        phyPayload_encoded = encodePhyPayload(phy_payload)
        self.gateway.up_link_publish(phyPayload_encoded)
        self.fCntUp += 1

    def send_data(self):
        if not self.active:
            return
        w_data = WatchdogData()
        w_data.battery = self.batteryLevel
        w_data.humidity = round(random.gauss(70, 20), 2)
        w_data.temperature = round(random.gauss(5, 6), 2)
        frame_payload = bytearray(base64.b64decode(w_data.encode_data()))

        dev_addr_byte = encodeDevAddr(int(self.dev_addr, 16).to_bytes(4, 'little'))
        ecrypted_frame_payload = encrypt_frm_payload(self.app_skey, self.net_skey, 1, True, dev_addr_byte, self.fCntUp,
                                                     frame_payload)
        ecrypted_frame_payload_encoded = base64.b64encode(ecrypted_frame_payload).decode()
        phy_payload = PhyPayload()
        # set MHDR
        phy_payload.mhdr.mType = MessageTypeEnum.UNCONFIRMED_DATA_UP.getName()
        phy_payload.mhdr.major = MajorTypeEnum.LoRaWANR1.getName()
        # set MacPayload
        macPaylaod = MacPayload()
        # set FHDR
        fhdr = FHDR()
        fhdr.devAddr = self.dev_addr
        fhdr.fCnt = self.fCntUp

        fhdr.fCtrl.adr = True

        macPaylaod.fhdr = fhdr
        macPaylaod.fPort = 1
        macPaylaod.frmPayload.append(Frame(ecrypted_frame_payload_encoded))

        phy_payload.macPayload = macPaylaod
        phy_payload.mic = "0"
        phy_payload_encoded = base64.b64decode(encodePhyPayload(phy_payload))
        phy_payload.mic = compute_data_mic(phy_payload_encoded, LorawanVersionEnum.LoRaWANR1_0.value, self.fCntUp, 0, 0,
                                           self.net_skey, True)
        phyPayload_encoded = encodePhyPayload(phy_payload)
        self.fCntUp += 1
        print("SEND DATA WATCHDOG: ", self.deviceName)
        self.gateway.up_link_publish(phyPayload_encoded)

    def __eq__(self, other):
        if not isinstance(other, Watchdog):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.applicationID.__eq__(other.applicationID) and \
               self.applicationName.__eq__(other.applicationName) and \
               self.applicationName.__eq__(other.applicationName) and \
               self.deviceName.__eq__(other.deviceName) and self.devEUI.__eq__(other.devEUI) and \
               self.margin.__eq__(other.margin) and self.externalPowerSource.__eq__(other.externalPowerSource) and \
               self.batteryLevelUnavailable.__eq__(other.batteryLevelUnavailable) and \
               self.batteryLevel.__eq__(other.batteryLevel) and self.tags.__eq__(other.tags) and \
               self.active.__eq__(other.active)

    def activate(self, phyPayload):
        join_accept_mac_payload = decode_join_accept_mac_payload(self.app_key, self.dev_nonce, phyPayload)
        self.net_skey = join_accept_mac_payload.nwk_SKey
        self.app_skey = join_accept_mac_payload.app_SKey
        self.app_nonce = join_accept_mac_payload.app_nonce
        self.net_ID = join_accept_mac_payload.net_ID
        self.dev_addr = join_accept_mac_payload.dev_addr
        self.batteryLevelUnavailable = False
        self.batteryLevel = 254
        self.margin = 31
        print(getJsonFromObject(join_accept_mac_payload))
        self.active = True

    def receive_message(self, phyPayload, txInfo):
        result = manage_received_message(self, phyPayload)
        self.txInfo = txInfo
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
        mac_command.cid = MacCommandEnum.DEVICE_STATUS_ANS.getName()
        frm_payload_encoded = encode_mac_commands_to_frm_payload(self.app_skey,
                                                                 self.net_skey, 0,
                                                                 True, self.dev_addr, self.fCntUp, [mac_command])
        # setting phy payload
        phy_payload = PhyPayload()
        phy_payload.mhdr.mType = MessageTypeEnum.UNCONFIRMED_DATA_UP.getName()
        phy_payload.mhdr.major = MajorTypeEnum.LoRaWANR1.getName()
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
        phy_payload_encoded = base64.b64decode(encodePhyPayload(phy_payload))
        phy_payload.mic = compute_data_mic(phy_payload_encoded, LorawanVersionEnum.LoRaWANR1_0.value, self.fCntUp, 0, 0,
                                           self.net_skey, True)
        phyPayload_encoded = encodePhyPayload(phy_payload)
        self.fCntUp += 1
        self.gateway.up_link_publish(phyPayload_encoded)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)
