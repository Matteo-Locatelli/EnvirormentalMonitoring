import unittest
from utils import coder, payload_util


class Test_coder(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("SetUp class")

    @classmethod
    def tearDownClass(cls):
        print("TearDown class")

    def setUp(self):
        print("SetUp")
        self.payloads = ["YKmbBwGgAQAA3s0o6XpEg709qE45mZK/hfM07NFXhiM=", "gKmbBwEANAEBhSve0Q==",
                    "YKmbBwGgAAAAuX0joM23ehlfKcOOpnv1iqLWLyDekH8=", "gKmbBwEANAEBhSve0Q=="]
        self.json1 = {
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
                    "fOpts": 0
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

    def tearDown(self):
        print("TearDown")


    def test_encodePhyPayload(self):
        self.assertNotEqual(self.payloads[0], coder.encodePhyPayloadFromJson(self.json1) ) # add assertion here

    def test_decodePhyPayload(self):
        self.assertNotEqual(payload_util.getJsonFromObject(coder.decodePhyPayload(self.payloads[0])), self.json1)

    def test_pay_payload(self):
        self.assertEqual(coder.decodePhyPayload(self.payloads[0]), coder.encodePhyPayloadFromJson(self.json1))

if __name__ == '__main__':
    unittest.main()
