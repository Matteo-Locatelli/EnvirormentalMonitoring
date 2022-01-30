import json
import base64
from paho.mqtt.client import Client

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


class edgeNode:
    # Number of gateways
    number_of_gw = 0
    conn_topic = "gateway/%s/state/conn"
    up_topic = "gateway/%s/event/up"
    down_topic = "gateway/%s/command/down"
    stats_topic = "gateway/%s/event/stats"

    def __init__(self,id_gateway,broker, port):
        self.client_id = "loragateway" + str(edgeNode.number_of_gw)
        self.username = "chirpstack_gw"
        self.password = ""
        self.id_gateway = id_gateway
        self.broker = broker
        self.port = port
        self.connect_mqtt()

    def connect_mqtt(self):
        # Set Connecting Client ID
        client = Client(client_id=self.client_id)
        client.username_pw_set(self.username, self.password)
        client.on_connect = on_connect
        client.on_connect_fail = on_connect_fail
        client.on_publish = on_publish
        client.on_disconnect = on_disconnect
        client.on_subscribe = on_subscribe
        client.on_message = on_message

        try:
            print("client connect", client.connect(self.broker, self.port, 60))
        except:
            print("ERROR: Could not connect to MQTT.")
        return client

    def conn_publish(self, client):
        conn_topic = edgeNode.conn_topic % self.id_gateway
        msg = 0
        result = client.publish(topic=conn_topic, payload=msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{conn_topic}`")
        else:
            print(f"Failed to send message to topic {conn_topic}")

    def stats_publish(self, client):
        stats_topic = edgeNode.stats_topic % self.id_gateway
        msg = 0
        result = client.publish(stats_topic, msg)
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{stats_topic}`")
        else:
            print(f"Failed to send message to topic {stats_topic}")

