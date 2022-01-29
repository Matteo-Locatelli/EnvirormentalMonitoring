from coder import decodePhyPayload, encodePhyPayload, encodePhyPayloadFromJson

payloads = ["QBj/XgAACAEB1efWJyP4IQZt84BwnYItoRQB", "QBj/XgAABwEBMBBkiV4q1N23Jv5I3sAE4x3y",
            "YBj/XgCAAQAAQK1X20rG6SZsDFdeCKDMaCr4vNdaqw==", "gAQDAgEAAAAB4mTU9yQHTwA=",
            "QBj/XgAABQEBjEq4EVxLInTagRIUG7WsR5Hz","IHWLMc5A2GfDYpR/y8/Nws13od6xWzo7b646OnXkh9/H"]

p = decodePhyPayload(payloads[5])
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

data = encodePhyPayloadFromJson(testPhy)

