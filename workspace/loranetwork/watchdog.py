import json

from downlink_message_manager import manageJoinAcceptRequest, check_message
from enums.mac_command_enum import MacCommandEnum
from enums.major_type_enum import MajorTypeEnum
from enums.message_type_enum import MessageTypeEnum
from payloads.mac_layer.mac_command_payload import MacCommandItem, MacCommandPayload
from payloads.mac_layer.phy_payload import PhyPayload
import random
import base64

from utils.coder import encodePhyPayload, decode_join_accept_mac_payload
from utils.payload_util import compute_join_request_mic, getJsonFromObject


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

#def getRandomData():

class Watchdog:
    def __init__(self, applicationID="", applicationName="", deviceName="", devEUI="", margin=None,
                 externalPowerSource=False, batteryLevelUnavailable=False, batteryLevel=None, tags=Tags(),
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
        self.fCntUp = 0 # da incrementare ad ogni invio
        self.fCntDown = 0 # da incrementare ogni ricezione
        self.data = []

    def join(self):
        phyPayload = PhyPayload()
        phyPayload.mhdr.mType = MessageTypeEnum.JOIN_REQUEST.getName()
        phyPayload.mhdr.major = MajorTypeEnum.LoRaWANR1.getName()
        phyPayload.macPayload.devEUI = self.devEUI
        phyPayload.macPayload.joinEUI = self.joinEUI
        self.dev_nonce = random.randint(10000, 30000)
        phyPayload.macPayload.devNonce = self.dev_nonce
        phyPayload.mic = "0"
        phyPayloadByte = base64.b64decode(encodePhyPayload(phyPayload))
        phyPayload.mic = compute_join_request_mic(phyPayloadByte, self.app_key)
        phyPayload_encoded = encodePhyPayload(phyPayload)
        self.gateway.up_link_publish(phyPayload_encoded)

    def send_data(self):
        if self.active:
            #può mandare dati, altrimenti NO

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
        print(getJsonFromObject(join_accept_mac_payload))
        self.active = True

    def receive_message(self, phyPayload):
        check_message(self, phyPayload)

    def send_device_status(self):
        mac_command = MacCommandItem()
        mac_command_payload = MacCommandPayload()
        mac_command_payload.margin = self.margin
        mac_command_payload.battery = self.batteryLevel
        mac_command.payload = mac_command_payload
        mac_command.cid = MacCommandEnum.DEVICE_STATUS_ANS.getName()
        

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)
