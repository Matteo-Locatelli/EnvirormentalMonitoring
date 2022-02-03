import unittest

from utils import coder, payload_util


class TestCoder(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n SetUp class")

    @classmethod
    def tearDownClass(cls):
        print("\n TearDown class")

    def setUp(self):
        print("\n SetUp")
        self.payloads = ["YKmbBwGgAQAA3s0o6XpEg709qE45mZK/hfM07NFXhiM=", "gKmbBwEANAEBhSve0Q==",
                         "YKmbBwGgAAAAuX0joM23ehlfKcOOpnv1iqLWLyDekH8=", "gKmbBwEANAEBhSve0Q=="]
        self.json0 = {
            "mhdr": {
                "mType": "UnconfirmedDataDown",
                "major": "LoRaWANR1"
            },
            "macPayload": {
                "fhdr": {
                    "devAddr": "01079ba9",
                    "fCtrl": {
                        "adr": True,
                        "adrAckReq": False,
                        "ack": True,
                        "fPending": False,
                        "classB": False
                    },
                    "fCnt": 1,
                    "fOpts": None
                },
                "fPort": 0,
                "frmPayload": [
                    {
                        "bytes": "3s0o6XpEg709qE45mZK/hfM07A=="
                    }
                ]
            },
            "mic": "d1578623"
        }

        self.json1 = {
            "mhdr": {
                "mType": "ConfirmedDataUp",
                "major": "LoRaWANR1"
            },
            "macPayload": {
                "fhdr": {
                    "devAddr": "01079ba9",
                    "fCtrl": {
                        "adr": False,
                        "adrAckReq": False,
                        "ack": False,
                        "fPending": False,
                        "classB": False
                    },
                    "fCnt": 308,
                    "fOpts": None
                },
                "fPort": 1,
                "frmPayload": None
            },
            "mic": "852bded1"
        }

        self.json2 = {
            "mhdr": {
                "mType": "UnconfirmedDataDown",
                "major": "LoRaWANR1"
            },
            "macPayload": {
                "fhdr": {
                    "devAddr": "01079ba9",
                    "fCtrl": {
                        "adr": True,
                        "adrAckReq": False,
                        "ack": True,
                        "fPending": False,
                        "classB": False
                    },
                    "fCnt": 0,
                    "fOpts": None
                },
                "fPort": 0,
                "frmPayload": [
                    {
                        "bytes": "uX0joM23ehlfKcOOpnv1iqLWLw=="
                    }
                ]
            },
            "mic": "20de907f"
        }

        self.json3 = {
            "mhdr": {
                "mType": "ConfirmedDataUp",
                "major": "LoRaWANR1"
            },
            "macPayload": {
                "fhdr": {
                    "devAddr": "01079ba9",
                    "fCtrl": {
                        "adr": False,
                        "adrAckReq": False,
                        "ack": False,
                        "fPending": False,
                        "classB": False
                    },
                    "fCnt": 308,
                    "fOpts": None
                },
                "fPort": 1,
                "frmPayload": []
            },
            "mic": "852bded1"
        }

        self.jsons = [self.json0, self.json1, self.json2, self.json3]

    def tearDown(self):
        print("\n TearDown")

    # Comparison between payloads in the format of Base64
    # encodePhyPayloadFromJSON: JSON -> Base64
    def test_encodePhyPayload(self):
        print("\n test_encodePhyPayload")
        self.assertEqual(self.payloads[0], coder.encodePhyPayloadFromJson(self.jsons[0]))
        self.assertEqual(self.payloads[1], coder.encodePhyPayloadFromJson(self.jsons[1]))
        self.assertEqual(self.payloads[2], coder.encodePhyPayloadFromJson(self.jsons[2]))
        self.assertEqual(self.payloads[3], coder.encodePhyPayloadFromJson(self.jsons[3]))

    # Comparison between JSONs of the payloads
    # decodePhyPayload: Base64 -> PhyPayload
    # getJSONFromObject: Object -> JSON
    # notEquals because the field 'f0pts' is removed from the decoded PhyPayload
    # JSON 0-2: differences in 'fOptsLen' and 'fOpts'
    # JSON 1-3: differences in 'fOptsLen' and 'fOpts' and 'frmPayload'
    def test_decodePhyPayload(self):
        print("\n test_decodePhyPayloads")
        self.assertNotEqual(payload_util.getJsonFromObject(coder.decodePhyPayload(self.payloads[0])), self.jsons[0])
        self.assertNotEqual(payload_util.getJsonFromObject(coder.decodePhyPayload(self.payloads[1])), self.jsons[1])
        self.assertNotEqual(payload_util.getJsonFromObject(coder.decodePhyPayload(self.payloads[2])), self.jsons[2])
        self.assertNotEqual(payload_util.getJsonFromObject(coder.decodePhyPayload(self.payloads[3])), self.jsons[3])

    # Comparison between PhyPayloads
    # decodePhyPayloads: Base64 -> PhyPayload
    # getPhyPayloadFromJson: JSON -> PhyPayload
    def test_phyPayload(self):
        print("\n test_payPhyload")
        self.assertEqual(coder.decodePhyPayload(self.payloads[0]), coder.getPhyPayloadFromJson(self.jsons[0]))
        self.assertEqual(coder.decodePhyPayload(self.payloads[1]), coder.getPhyPayloadFromJson(self.jsons[1]))
        self.assertEqual(coder.decodePhyPayload(self.payloads[2]), coder.getPhyPayloadFromJson(self.jsons[2]))
        self.assertEqual(coder.decodePhyPayload(self.payloads[3]), coder.getPhyPayloadFromJson(self.jsons[3]))


if __name__ == '__main__':
    unittest.main()
