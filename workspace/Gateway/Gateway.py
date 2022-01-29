# import
import base64
import random
import time
from datetime import datetime
import json
from paho.mqtt.client import Client
import base64

# indirizzo IP broker
broker = "172.22.59.140"
port = 1883;

# client_id
client_id = "mosq-pyGateway"
username = "chirpstack_gw"
password = ""
netSessionKey = "16826413ee7294311369e4c3a2ce772f"

# topic
conn_topic = "gateway/f23ad78a721d2334/state/conn"
config_topic = "gateway/f23ad78a721d2334/device/configuration/indirizzo_device"
up_topic = "gateway/f23ad78a721d2334/event/up"
join_topic = "gateway/f23ad78a721d2334/event/join"
stats_topic = "gateway/f23ad78a721d2334/event/stats"

# gateway id
idGateway = "f23ad78a721d2334"
encodedIdGateway = base64.b64encode(int(idGateway, 16).to_bytes(8, 'big')).decode()

# payloads
conn_payload = {
    "gatewayID": encodedIdGateway,
    "state": "ONLINE"
}

testPhy = {
    "mes": "hello"
}

testB = json.dumps(testPhy)
up_payload = {
    "phyPayload": json.dumps(testPhy),
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


def connect_mqtt():
    # Set Connecting Client ID
    client = Client(client_id=client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_connect_fail = on_connect_fail
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
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
    msg = json.dumps(up_payload)
    result = client.publish(up_topic, msg)
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{up_topic}`")
    else:
        print(f"Failed to send message to topic {up_topic}")


def up_publish(client):
    msg = json.dumps(up_payload)
    result = client.publish(up_topic, msg)

    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{up_topic}`")
    else:
        print(f"Failed to send message to topic {up_topic}")


def run():
    client = connect_mqtt()
    time.sleep(2)
    client.loop_start()
    while not client.is_connected():  # wait in loop
        print("In wait loop")
        time.sleep(1)
    print("in Main Loop")
    time.sleep(1)
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
    client.loop_stop()
    client.disconnect()


if __name__ == '__main__':
    run()
