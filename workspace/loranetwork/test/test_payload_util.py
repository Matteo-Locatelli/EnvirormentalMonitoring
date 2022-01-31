import unittest

from utils import payload_util, coder


class TestPayloadUtil(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n SetUp class")

    @classmethod
    def tearDownClass(cls):
        print("\n TearDown class")

    def setUp(self):
        print("\n SetUp")

        self.appKey = "a772a9b9c627b3a41370b8a8646e6e80"

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

        self.mic0 = "d1578623"

    def tearDown(self):
        print("\n TearDown")

    def test_compute_join_request_mic(self):
        print("\n Test Compute Join Request Mic")
        self.assertEqual(payload_util.compute_join_request_mic(coder.getPhyPayloadFromJson(self.json0), self.appKey), self.mic0)


if __name__ == '__main__':
    unittest.main()
