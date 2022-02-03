import base64
import json

from utils.payload_util import getJsonFromObject


class WatchdogData():
    humidity = 0
    temperature = 0
    battery = 100

    def __init__(self):
        self.humidity = 0
        self.temperature = 0
        self.battery = 0

    def encode_data(self):
        json_data = getJsonFromObject(self)
        json_string_data = json.dumps(json_data)
        json_string_encoded_data = json_string_data.encode()
        b64_encoded_data = base64.b64encode(json_string_encoded_data)  # array di byte in base64
        return b64_encoded_data.decode()

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)
