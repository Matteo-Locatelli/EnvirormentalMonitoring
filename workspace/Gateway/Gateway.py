# import
import base64
import random
import time
from datetime import datetime
import json
from paho.mqtt.client import Client

# indirizzo IP broker
broker = "172.28.225.99"
port = 1883;

# random client_id
client_id = "mosq-pyGateway"
username = "chirpstack_gw"
password = ""

# topic
conn_topic = "gateway/f23ad78a721d2334/state/conn"
up_topic = "gateway/f23ad78a721d2334/event/up"
stats_topic = "gateway/f23ad78a721d2334/event/stats"

# payloads
conn_payload = {
    "gatewayID": "f23ad78a721d2334",
    "state": "ONLINE"
}

join_payload = {
    "rxInfo": [
        {
            "gatewayID": "f23ad78a721d2334",
            "time": datetime.now().strftime("%H:%M:%S"),
            "timeSinceGPSEpoch": "1326832.347s",
            "rssi": -60,
            "loRaSNR": 7,
            "channel": 0,
            "rfChain": 0,
            "board": 0,
            "antenna": 0,
            "location": {
                "latitude": 45.64721335397582,
                "longitude": 9.597843157441028,
                "altitude": 0,
                "source": "UNKNOWN",
                "accuracy": 0
            },
            "fineTimestampType": "NONE",
            "context": "YesPui==",
            "uplinkID": str(str(datetime.now()).encode()),
            "crcStatus": "CRC_OK"
        }
    ],
    "txInfo": {
        "frequency": 433175000,
        "modulation": "LORA",
        "loRaModulationInfo": {
            "bandwidth": 125,
            "spreadingFactor": 7,
            "codeRate": "4/5",
            "polarizationInversion": False
        }
    },
    "phyPayload": {
        "mhdr": {
            "mType": "JoinRequest",
            "major": "LoRaWANR1"
        },
        "macPayload": {
            "joinEUI": "0000000000000000",
            "devEUI": "0ac14aad3e6391a1",
            "devNonce": 3447
        },
        "mic": "0a25de1f"
    }
}

stats_payload = {
    "gatewayID": "f23ad78a721d2334",
    "time": "2022-01-02T15:04:05.999999999Z",
    "ip": "172.16.209.108",
    "location": {
        "latitude": 45.64721335397582,
        "longitude": 9.597843157441028,
        "altitude": 0,
        "source": "UNKNOWN",
        "accuracy": 0
    },
    "configVersion": "1.2.3",
    "rxPacketsReceived": 0,
    "rxPacketsReceivedOK": 0,
    "txPacketsReceived": 0,
    "txPacketsEmitted": 1
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
    msg = json.dumps(stats_payload)
    result = client.publish(stats_topic, msg)
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{stats_topic}`")
    else:
        print(f"Failed to send message to topic {stats_topic}")


def up_publish(client):
    packettosend = {
        "confirmed": False,
        "fPort": 1,
        "data": "hello"
    }

    json_packet_to_send = json.dumps(packettosend)
    msg = 1
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
    time.sleep(2)
    conn_publish(client)
    j = 1
    while j == 1:
        time.sleep(2)
        j = int(input('Inserisci 0 per terminare: '))

    i = 0;
    while i < 10 and j == 2:
        time.sleep(1)
        stats_publish(client)
        i += 1

    client.loop_stop()
    client.disconnect()


if __name__ == '__main__':
    run()
