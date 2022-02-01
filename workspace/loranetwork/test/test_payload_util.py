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
        self.appSKey = "49B9A84A87C8739345CFE0E710C415BD"
        self.netSKey = "9124E280A8E0645ABE6974DF43E029B8"
        self.LoRaWANR1_0 = "LoRaWANR1"

        # Join request
        self.payload_join_request = "AAAAAAAAAAAAoZFjPq1KwQofzd9qzRI="

        # Join accept
        self.payload_join_accept = "IKGT2fFHOFY3V17VpslbSz+deWV05XJwRPti54vmD6Nw"

        # Compute uplink
        self.payload_compute_uplink_con = "gKmbBwEANAEBhSve0Q=="
        self.payload_compute_uplink_unc = "YKmbBwGgAQAA3s0o6XpEg709qE45mZK/hfM07NFXhiM="

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

        # Payload compute uplink confirmed data up
        self.json_compute_uplink_con = {
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

        # Payload compute uplink unconfirmed data down
        self.json_compute_uplink_unc = {
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

        # Mic compute uplink
        self.mic_compute_uplink_con = self.json_compute_uplink_con['mic']
        self.mic_compute_uplink_unc = self.json_compute_uplink_unc['mic']

        # Mic join request
        self.mic_join_request = self.json_join_request['mic']

        # Mic join accept
        self.mic_join_accept = self.json_join_accept['mic']


    def tearDown(self):
        print("\n TearDown")

    # Comparison between the mic in the JSON "join_request" object and the mic computed by the function
    # compute_join_request_mic
    # @ Parameters: appKey: static
    # @ Parameter: payload_join_request converted in hexadecimal number with b64decode
    def test_compute_join_request_mic(self):
        print("\n Test Compute Join Request Mic")
        self.assertEqual(
            payload_util.compute_join_request_mic(base64.b64decode(self.payload_join_request), self.appKey),
            self.mic_join_request)

    # Comparison between the mic in the JSON "compute_uplink" object and the mic computed by the function
    # compute_uplink_data_mic
    # @ Parameter: payload_compute_uplink converted in hexadecimal number with b64decode
    def test_compute_uplink_data_mic(self):
        print("\n Test Compute Uplink Data Mic")
        self.assertEqual(
            payload_util.compute_uplink_data_mic(base64.b64decode(self.payload_compute_uplink_con), self.LoRaWANR1_0,
                                                 308, 0, 0, self.netSKey), self.mic_compute_uplink_con)
        #self.assertEqual(
        #    payload_util.compute_uplink_data_mic(base64.b64decode(self.payload_compute_uplink_unc), self.LoRaWANR1_0,
        #                                         1, 0, 0, self.appKey), self.mic_compute_uplink_unc)

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
