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

        self.json_list = [self.json0, self.json1, self.json2, self.json3]

    def tearDown(self):
        print("\n TearDown")

    # Comparison between payloads in the format of Base64
    # encode_phy_payload_from_json: JSON -> Base64
    def test_encode_phy_payload(self):
        print("\n test_encode_phy_payload")
        self.assertEqual(self.payloads[0], coder.encode_phy_payload_from_json(self.json_list[0]))
        self.assertEqual(self.payloads[1], coder.encode_phy_payload_from_json(self.json_list[1]))
        self.assertEqual(self.payloads[2], coder.encode_phy_payload_from_json(self.json_list[2]))
        self.assertEqual(self.payloads[3], coder.encode_phy_payload_from_json(self.json_list[3]))

    # Comparison between JSONs of the payloads
    # decode_phy_payload: Base64 -> PhyPayload
    # getJSONFromObject: Object -> JSON
    # notEquals because the field 'f0pts' is removed from the decoded PhyPayload
    # JSON 0-2: differences in 'fOptsLen' and 'fOpts'
    # JSON 1-3: differences in 'fOptsLen' and 'fOpts' and 'frmPayload'
    def test_decode_phy_payload(self):
        print("\n test_decodePhyPayloads")
        self.assertNotEqual(payload_util.get_json_from_object(coder.decode_phy_payload(self.payloads[0])), self.json_list[0])
        self.assertNotEqual(payload_util.get_json_from_object(coder.decode_phy_payload(self.payloads[1])), self.json_list[1])
        self.assertNotEqual(payload_util.get_json_from_object(coder.decode_phy_payload(self.payloads[2])), self.json_list[2])
        self.assertNotEqual(payload_util.get_json_from_object(coder.decode_phy_payload(self.payloads[3])), self.json_list[3])

    # Comparison between PhyPayloads
    # decode_phy_payload: Base64 -> PhyPayload
    # get_phy_payload_from_json: JSON -> PhyPayload
    def test_phy_payload(self):
        print("\n decode_phy_payload")
        self.assertEqual(coder.decode_phy_payload(self.payloads[0]), coder.get_phy_payload_from_json(self.json_list[0]))
        self.assertEqual(coder.decode_phy_payload(self.payloads[1]), coder.get_phy_payload_from_json(self.json_list[1]))
        self.assertEqual(coder.decode_phy_payload(self.payloads[2]), coder.get_phy_payload_from_json(self.json_list[2]))
        self.assertEqual(coder.decode_phy_payload(self.payloads[3]), coder.get_phy_payload_from_json(self.json_list[3]))


if __name__ == '__main__':
    unittest.main()
