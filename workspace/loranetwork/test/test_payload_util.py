import base64
import unittest

from utils import payload_util


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
        self.netSKey = "1F5572B62B9052AC821BBDFF92DC09B2"
        self.appSKey = "796D28D4F849ABFF68656E6671D833F3"
        self.LoRaWANR1_0 = "LoRaWANR1"

        # Join request
        self.payloadJoinRequest = "AAAAAAAAAAAAoZFjPq1KwQofzd9qzRI="

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

        self.mic_join_request = self.json_join_request['mic']

        # Join accept
        self.payload_join_accept = "IKGT2fFHOFY3V17VpslbSz+deWV05XJwRPti54vmD6Nw"

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

        self.mic_join_accept = self.json_join_accept['mic']

        # Compute data
        self.payload_compute_data = "QPt/dgEABQABYVH7mg=="

        self.json_compute_data = {
            "mhdr": {
                "mType": "UnconfirmedDataUp",
                "major": "LoRaWANR1"
            },
            "macPayload": {
                "fhdr": {
                    "devAddr": "01767ffb",
                    "fCtrl": {
                        "adr": False,
                        "adrAckReq": False,
                        "ack": False,
                        "fPending": False,
                        "classB": False
                    },
                    "fCnt": 5,
                    "fOpts": None
                },
                "fPort": 1,
                "frmPayload": []
            },
            "mic": "6151fb9a"
        }

        self.mic_compute_data = self.json_compute_data['mic']

        self.fCnt_compute_data = self.json_compute_data["macPayload"]["fhdr"]["fCnt"]

    def tearDown(self):
        print("\n TearDown")

    # Comparison between the mic in the JSON "join_request" object and the mic computed by the function
    # compute_join_request_mic
    # @ Parameters: appKey: static
    # @ Parameter: payloadJoinRequest converted in hexadecimal number with b64decode
    def test_compute_join_request_mic(self):
        print("\n Test Compute Join Request Mic")
        self.assertEqual(
            payload_util.compute_join_request_mic(base64.b64decode(self.payloadJoinRequest), self.appKey),
            self.mic_join_request)

    # Comparison between the mic in the JSON "compute_data" object and the mic computed by the function
    # compute_data_mic
    # @ Parameter: payload_compute_uplink converted in hexadecimal number with b64decode
    # @ Parameter: netSKey is the network session key and MUST BE CHANGED at each execution
    def test_compute_data_mic(self):
        print("\n Test Compute Uplink Data Mic")
        self.assertEqual(
            payload_util.compute_data_mic(base64.b64decode(self.payload_compute_data.encode()), self.LoRaWANR1_0,
                                          self.fCnt_compute_data, 0, 0, self.netSKey, True),
            self.mic_compute_data)

    # Comparison between the mic in the JSON "join_accept" object and the mic computed by the function
    # compute_join_accept_mic
    # @ Parameters: appKey: static
    # @ Parameter: payload_join_accept converted in hexadecimal number with b64decode
    def test_compute_join_accept_mic(self):
        print("\n Test Compute Join Accept Mic")
        self.assertEqual(
            payload_util.compute_join_accept_mic(base64.b64decode(self.payload_join_accept), self.appKey),
            self.mic_join_accept)


if __name__ == '__main__':
    unittest.main()
