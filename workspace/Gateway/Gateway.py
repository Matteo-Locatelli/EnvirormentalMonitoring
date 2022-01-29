# import
import time
import json
import base64
from paho.mqtt.client import Client
import random
from Crypto.Hash import CMAC
from Crypto.Cipher import AES
from PhyPayload import PhyPayload
from coder import encodePhyPayloadFromJson, encodePhyPayload
from phy_payload_util import compute_join_request_mic, compute_uplink_data_mic

# indirizzo IP broker
broker = "172.22.59.140"
port = 1883;

# client_id
client_id = "mosq-pyGateway"
username = "chirpstack_gw"
password = ""
netSessionKey = "3cf0d4d88407fe11f2a9f2a125249b9f"
appKey = "a772a9b9c627b3a41370b8a8646e6e80"
appKeyByte = bytearray([0xa7, 0x72, 0xa9, 0xb9, 0xc6, 0x27, 0xb3, 0xa4, 0x13, 0x70, 0xb8, 0xa8, 0x64, 0x6e, 0x6e, 0x80])
appSkeyByte = bytearray([0xcc, 0x12, 0x5c, 0x2e, 0x6d, 0xec, 0xe0, 0xd0, 0x3d, 0x0f, 0xef, 0x8f, 0x3b, 0xe3, 0xe0, 0x9a])
#appSkeyByte = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
# gateway id
idGateway = "f23ad78a721d2334"
encodedIdGateway = base64.b64encode(int(idGateway, 16).to_bytes(8, 'big')).decode()

# topic
conn_topic = "gateway/" + idGateway + "/state/conn"
config_topic = "gateway/" + idGateway + "/device/configuration/indirizzo_device"
up_topic = "gateway/" + idGateway + "/event/up"
down_topic = "gateway/" + idGateway + "/command/down"
stats_topic = "gateway/" + idGateway + "/event/stats"

# Message types
JOIN_REQUEST = "JoinRequest"
JOIN_ACCEPT = "JoinAccept"
UNCONFIRMED_DATA_UP = "UnconfirmedDataUp"
UNCONFIRMED_DATA_DOWN = "UnconfirmedDataDown"
CONFIRMED_DATA_UP = "ConfirmedDataUp"
CONFIRMED_DATA_DOWN = "ConfirmedDataDown"

# Major
LoRaWANR1 = "LoRaWANR1"
LoRaWANR0 = "LoRaWANR0"

# Device data
devEUI = "0ac14aad3e6391a1"
joinEUI = "0000000000000000"
devNonce = random.randint(10000, 20000)

# payloads
conn_payload = {
    "gatewayID": encodedIdGateway,
    "state": "ONLINE"
}

testPhy = {
    "mhdr": {
        "mType": "ConfirmedDataUp",
        "major": "LoRaWANR1"
    },
    "macPayload": {
        "fhdr": {
            "devAddr": "01020304",
            "fCtrl": {
                "adr": False,
                "adrAckReq": False,
                "ack": False,
                "fPending": False,
                "classB": False
            },
            "fCnt": 0
        },
        "fPort": 10,
        "frmPayload": [
            {
                "bytes": "4mTU9w=="
            }
        ]
    },
    "mic": "e117d2c0"
}

up_payload = {
    "phyPayload": "",
    "txInfo": {
        "frequency": 922200000,
        "modulation": "LORA",
        "loRaModulationInfo": {
            "bandwidth": 125,
            "spreadingFactor": 7,
            "codeRate": "4/5",
            "polarizationInversion": False
        }
    },
    "rxInfo": {
        "gatewayID": encodedIdGateway,
        "rssi": -60,
        "loRaSNR": 7,
        "channel": 3,
        "rfChain": 0,
        "board": 0,
        "antenna": 0,
        "location": None,
        "fineTimestampType": "NONE",
        "context": "YfM77Q==",
        "uplinkID": "Cg0mctELRZLfVSHPNQKPqw==",
        "crcStatus": "CRC_OK"
    }
}

stats_payload = {
    "gatewayID": encodedIdGateway,
    "ip": "172.21.185.160",
    "time": "2022-01-27T20:12:23Z",
    "location": None,
    "configVersion": "",
    "rxPacketsReceived": 2,
    "rxPacketsReceivedOK": 0,
    "txPacketsReceived": 3,
    "txPacketsEmitted": 0,
    "metaData": {},
    "statsID": "JCjPH3pARfeWnuGpcdn1jA==",
    "txPacketsPerFrequency": {},
    "rxPacketsPerFrequency": {},
    "txPacketsPerModulation": [],
    "rxPacketsPerModulation": [],
    "txPacketsPerStatus": {}
}

canSendData = False


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True
        print("connected OK Returned code=", rc)
    else:
        print("Bad connection Returned code=", rc)


def on_connect_fail():
    print("connection failed")


def on_publish(client, userdata, mid):
    print("Message pubblished", mid)


def on_disconnect(client, userdata, rc):
    print("client disconnected ok")


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed to topic ", mid)


def on_message(client, userdata, msg):
    global canSendData
    print("Received message: ", msg.payload, " from topic: ", msg.topic)
    canSendData = True
    print(msg.payload.decode("utf-8"))


def connect_mqtt():
    # Set Connecting Client ID
    client = Client(client_id=client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_connect_fail = on_connect_fail
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    try:
        print("client connect", client.connect(broker, port, 60))
    except:
        print("ERROR: Could not connect to MQTT.")
    return client


def conn_publish(client):
    msg = json.dumps(conn_payload)
    result = client.publish(topic=conn_topic, payload=msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{conn_topic}`")
    else:
        print(f"Failed to send message to topic {conn_topic}")


def stats_publish(client):
    msg = json.dumps(stats_payload).encode("utf-8")
    result = client.publish(stats_topic, msg)
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{stats_topic}`")
    else:
        print(f"Failed to send message to topic {stats_topic}")


def up_publish(client):
    up_payload['phyPayload'] = encodePhyPayloadFromJson(testPhy)
    msg = json.dumps(up_payload)
    result = client.publish(up_topic, msg)

    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{up_topic}`")
    else:
        print(f"Failed to send message to topic {up_topic}")


def join_request_publish(client):
    phyPayload = PhyPayload()
    phyPayload.mhdr.mType = JOIN_REQUEST
    phyPayload.mhdr.major = LoRaWANR1
    phyPayload.macPayload.devEUI = devEUI
    phyPayload.macPayload.joinEUI = joinEUI
    phyPayload.macPayload.devNonce = devNonce
    phyPayload.mic = "0"
    phyPayloadByte = base64.b64decode(encodePhyPayload(phyPayload))
    phyPayload.mic = compute_join_request_mic(phyPayloadByte, appKey)  # non ancora funzionante questo

    up_payload['phyPayload'] = encodePhyPayload(phyPayload)
    msg = json.dumps(up_payload)
    result = client.publish(up_topic, msg)

    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{up_topic}`")
    else:
        print(f"Failed to send message to topic {up_topic}")


def subscribe(client):
    client.subscribe(down_topic)


def run():
    global canSendData
    client = connect_mqtt()
    time.sleep(2)
    client.loop_start()
    while not client.is_connected():  # wait in loop
        print("In wait loop")
        time.sleep(1)
    print("in Main Loop")
    time.sleep(1)
    subscribe(client)
    join_request_publish(client)
    j = 0
    while not canSendData and j < 4:
        print("Wait for join accept")
        time.sleep(10)
        j += 1

    if canSendData:
        j = 2
        while j == 1:
            time.sleep(1)
            j = int(input('Inserisci 0 per terminare: '))

        i = 0;
        while i < 1 and j == 2:
            time.sleep(1)
            stats_publish(client)
            i += 1

        time.sleep(1)
        up_publish(client)
    else:
        print("JoinRequest failed")
    client.loop_stop()
    client.disconnect()


if __name__ == '__main__':
    run()
