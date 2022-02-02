# humidity
# temperature = rand(0:10)
# battery
import random
import json
import base64

class WatchdogData():
    humidity = 0
    temperature = 0
    battery = 100

    def __init__(self):
        self.humidity = random.random() * 100
        self.temperature = random.randint(-10, 40)
        self.battery = random.randint(0, 100)

    def encode_data(self):
        json_data = {
            "humidity" : self.humidity,
            "temperature" : self.temperature,
            "battery" : self.battery
        }
        json_string_data = json.dumps(json_data)
        json_string_encoded_data = json_string_data.encode()
        # b64_encoded_data = base64.b64encode(json_string_encoded_data) array di byte
        b64_decoded_data = base64.b64encode(json_string_encoded_data).decode() # Stringa codificata in base 64
        return b64_decoded_data


