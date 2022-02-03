from enums.message_type_enum import MessageTypeEnum
from utils.coder import decodePhyPayload, encodePhyPayloadFromJson, \
    decode_frm_payload_to_mac_commands, decode_fopts_payload_to_mac_commands
from utils.payload_util import getJsonFromObject

appKey = "a772a9b9c627b3a41370b8a8646e6e80"
appSKey = "49B9A84A87C8739345CFE0E710C415BD"
netSKey = "9124E280A8E0645ABE6974DF43E029B8"

appKB = bytearray([16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
payloads = ["QBj/XgAACAEB1efWJyP4IQZt84BwnYItoRQB", "QBj/XgAABwEBMBBkiV4q1N23Jv5I3sAE4x3y",
            "YBj/XgCAAQAAQK1X20rG6SZsDFdeCKDMaCr4vNdaqw==", "gAQDAgEAAAAB4mTU9yQHTwA=",
            "QBj/XgAABQEBjEq4EVxLInTagRIUG7WsR5Hz", "IHWLMc5A2GfDYpR/y8/Nws13od6xWzo7b646OnXkh9/H",
            "YNsYlgGgAwAAGrqJ/zsoFt14PfBHAtlnItU1mCQrl/8=", "gAQDAgEDAAAGcwcK4mTU9+EX0sA=",
            "YHNUcACgAAAAzWFT3ZMc/A9otKSGoQ33kg/Z80K4hBk="]

p = decodePhyPayload("YKmbBwGgAQAA3s0o6XpEg709qE45mZK/hfM07NFXhiM=")
print(getJsonFromObject(p))
testPhy = {
    "mhdr": {
        "mType": "ConfirmedDataUp",
        "major": "LoRaWANR1"
    },
    "macPayload": {
        "fhdr": {
            "devAddr": "01020304",
            "fCtrl": {
                "adr": False,
                "adrAckReq": False,
                "ack": False,
                "fPending": False,
                "classB": False
            },
            "fCnt": 0
        },
        "fPort": 10,
        "frmPayload": [
            {
                "bytes": "4mTU9w=="
            }
        ]
    },
    "mic": "e117d2c0"
}
print(getJsonFromObject(p))
mac_command_payload_list_fopts = decode_fopts_payload_to_mac_commands(
    MessageTypeEnum.findByName(p.mhdr.mType).isUplink(), p.macPayload.fhdr.fOpts)
for mac_command_payload_fopts in mac_command_payload_list_fopts:
    print(getJsonFromObject(mac_command_payload_fopts))

mac_command_payload_list_frmpl = decode_frm_payload_to_mac_commands(appKey,
                                                                    MessageTypeEnum.findByName(p.mhdr.mType).isUplink(),
                                                                    p.macPayload.fhdr.devAddr,
                                                                    p.macPayload.fhdr.fCnt,
                                                                    p.macPayload.frmPayload)
for mac_command_payload_frmpl in mac_command_payload_list_frmpl:
    print(getJsonFromObject(mac_command_payload_frmpl))

data = encodePhyPayloadFromJson(testPhy)
