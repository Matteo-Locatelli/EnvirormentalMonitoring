# import
import random
import time
from datetime import datetime
import json
from paho.mqtt.client import Client

# indirizzo IP broker
broker = "localhost"
port = 1883;

# topic
up_topic = "application/1/device/0ac14aad3e6391a1/event/up"
join_topic = "application/1/device/0ac14aad3e6391a1/event/join"

# payload
up_payload_object ={
    "applicationID": "1",
    "applicationName": "test-chirpstack-application",
    "deviceName": "Device-1",
    "devEUI": "0ac14aad3e6391a1",
    "rxInfo": [
        {
            "gatewayID": "1f6aa45e9ed77a78",
            "time":datetime.now().strftime("%H:%M:%S"),
            "timeSinceGPSEpoch": "null",
            "rssi": -48,
            "loRaSNR": 9,
            "channel": 5,
            "rfChain": 0,
            "board": 0,
            "antenna": 0,
            "location": {
                "latitude": 45.64721335397582,
                "longitude": 9.597843157441028,
                "altitude": 0
            },
            "fineTimestampType": "NONE",
            "context": "Yd+Gog==",
            "uplinkID": "jhMh8Gq6RAOChSKbi83RHQ=="
        }
    ],
    "txInfo": {
        "frequency": 868100000,
        "modulation": "LORA",
        "loRaModulationInfo": {
            "bandwidth": 125,
            "spreadingFactor": 11,
            "codeRate": "4/5",
            "polarizationInversion": "false"
        }
    },
    "adr": "true",
    "dr": 1,
    "fCnt": 10,
    "fPort": 5,
    "data": "...",
    "objectJSON": "{\"temperatureSensor\":25,\"humiditySensor\":32}",
    "tags": {
        "key": "value"
    }
}
join_payload_object = {
    "applicationID": "1",
    "applicationName": "test-chirpstack-application",
    "deviceName": "Device-1",
    "devEUI": "0ac14aad3e6391a1",
    "devAddr": "59 7c 6a 01",
    "rxInfo": [
        {
            "gatewayID": "1f6aa45e9ed77a78",
            "time":datetime.now().strftime("%H:%M:%S"),
            "timeSinceGPSEpoch": "null",
            "rssi": -48,
            "loRaSNR": 9,
            "channel": 5,
            "rfChain": 0,
            "board": 0,
            "antenna": 0,
            "location": {
                "latitude": 45.64721335397582,
                "longitude": 9.597843157441028,
                "altitude": 0
            },
            "fineTimestampType": "NONE",
            "context": "9u/uvA==",
            "uplinkID": "jhMh8Gq6RAOChSKbi83RHQ=="
        }
    ],
    "txInfo": {
        "frequency": 923000000,
        "modulation": "LORA",
        "loRaModulationInfo": {
            "bandwidth": 125,
            "spreadingFactor": 11,
            "codeRate": "4/5",
            "polarizationInversion": "false"
        }
    },
    "dr": 1,
    "tags": {
        "key": "value"
    }
}
# random client_id
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = ""
password = ""

def connect_mqtt():
    def on_connect(rc):
        print("Connected",rc)

    # Set Connecting Client ID
    client = Client(client_id=client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect

    print("client connect", client.connect(broker, port, 60, "0.0.0.0"))
    return client


def publish(client):
    msg_count = 0
    while True:
        time.sleep(10)
        msg = f"messages: {msg_count}"
        result = client.publish(topic=up_topic, payload=msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{up_topic}`")
        else:
            print(f"Failed to send message to topic {up_topic}")
        msg_count += 1


def join_publish(client):
    msg_count = 0
    global join_payload_object
    time.sleep(1)
    msg = json.dumps(join_payload_object)
    result = client.publish(topic=join_topic, payload=msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
       print(f"Send `{msg}` to topic `{join_topic}`")
    else:
       print(f"Failed to send message to topic {join_topic}")
    msg_count += 1


def run():
    client = connect_mqtt()
    print(client.is_connected())
    if(client.is_connected()):
        client.loop_start()
        publish(client)


if __name__ == '__main__':
    run()
