import base64
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
        self.LoRaWANR1_0 = "LoRaWANR1"
        self.devEUI = "0ac14aad3e6391a1"
        self.netSessionKey = "3cf0d4d88407fe11f2a9f2a125249b9f"

        # Join request
        self.payload_join_request = "AAAAAAAAAAAAoZFjPq1KwQofzd9qzRI="

        # Join accept
        self.payload_join_accept = "IKGT2fFHOFY3V17VpslbSz+deWV05XJwRPti54vmD6Nw"

        # Compute uplink
        self.payload_compute_uplink = "gKmbBwEANAEBhSve0Q=="

        # Payload join request
        self.json_join_request = {
            "mhdr": {
                "mType": "JoinRequest",
                "major": "LoRaWANR1"
            },
            "macPayload": {
                "joinEUI": "0000000000000000",
                "devEUI": "0ac14aad3e6391a1",
                "devNonce": 52511
            },
            "mic": "df6acd12"
        }

        # Payload join accept
        self.json_join_accept = {
            "mhdr": {
                "mType": "JoinAccept",
                "major": "LoRaWANR1"
            },
            "macPayload": {
                "bytes": "oZPZ8Uc4VjdXXtWmyVtLP515ZXTlcnBE+2Lniw=="
            },
            "mic": "e60fa370"
        }

        # Payload compute uplink
        self.json_compute_uplink = {
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

        # Mic compute uplink
        self.mic_compute_uplink = self.json_compute_uplink['mic']

        # Mic join request
        self.mic_join_request = self.json_join_request['mic']

        # Mic join accept
        self.mic_join_accept = self.json_join_accept['mic']

    def tearDown(self):
        print("\n TearDown")

    # Comparison between the mic in the JSON object and the mic computed by the function compute_join_request_mic
    # @ Parameters: appKey: static
    # @ Parameter: payload_join_request converted in hexadecimal number with b64decode
    def test_compute_join_request_mic(self):
        print("\n Test Compute Join Request Mic")
        self.assertEqual(
            payload_util.compute_join_request_mic(base64.b64decode(self.payload_join_request), self.appKey),
            self.mic_join_request)
        # self.assertNotEqual(payload_util.compute_join_request_mic(base64.b64decode(self.payload_join_accept), self.appKey),self.mic_join_accept)

    # @ Parameter: payload_join_request converted in hexadecimal number with b64decode
    def test_compute_uplink_data_mic(self):
        print("\n Test Compute Uplink Data Mic")
        self.assertEqual(
            payload_util.compute_uplink_data_mic(base64.b64decode(self.payload_compute_uplink), self.LoRaWANR1_0, 308, 0, 0,
                                                 self.appKey), self.mic_compute_uplink)


if __name__ == '__main__':
    unittest.main()
