import json
import base64
import time
import random
from typing import TypeVar

from paho.mqtt.client import Client
from datetime import datetime

from enums.crc_status_enum import CRCStatusEnum
from enums.tx_ack_status_enum import TxAckStatusEnum
from payloads.info.rx_info import RxInfo
from payloads.info.tx_info import TxInfo
from payloads.tx_ack_item_payload import TxAckItemPayload
from payloads.tx_ack_payload import TxAckPayload
from payloads.up_payload import UpPayload
from utils.payload_util import getJsonFromObject

# Payload message types
from payloads.conn_payload import ConnPayload
from payloads.stats_payload import StatsPayload
from enums.connection_state_enum import ConnectionStateEnum

T = TypeVar('T')

"""""
def get_up_payload(message_type, major_type, phy_payload):
    p = PhyPayload()
    p.mhdr.mType = message_type.getName()
    p.mhdr.major = major_type.getName()
    #p.macPayload.fhdr.devAddr = json_packet['macPayload']['fhdr']['devAddr']
    p.macPayload.fhdr.fCtrl.ADR = False
    p.macPayload.fhdr.fCtrl.ADRACKReq = False
    p.macPayload.fhdr.fCtrl.ACK = False
    p.macPayload.fhdr.fCtrl.FPending = False
    p.macPayload.fhdr.fCtrl.ClassB = False
    p.macPayload.fhdr.fCnt = 0
    p.macPayload.fPort = 0
"""""


class EdgeNode:
    # Number of gateways
    number_of_gw = 0
    conn_topic = "gateway/%s/state/conn"
    up_topic = "gateway/%s/event/up"
    ack_topic = "gateway/%s/event/ack"
    down_topic = "gateway/%s/command/down"
    stats_topic = "gateway/%s/event/stats"

    def __init__(self, broker, port, id_gateway, ip="localhost"):
        self.broker = broker
        self.port = port
        self.ip = ip
        self.client_id = "loragateway" + str(EdgeNode.number_of_gw)
        self.username = "chirpstack_gw"
        self.password = ""
        self.id_gateway = id_gateway
        self.encoded_id_gateway = base64.b64encode(int(id_gateway, 16).to_bytes(8, 'big')).decode()
        self.can_sand_data = False
        self.client = None
        self.rxPacketsReceived = 1  # Number of radio packets received.
        self.rxPacketsReceivedOK = 0  # Number of radio packets received with valid PHY CRC.
        self.txPacketsReceived = 0  # Number of downlink packets received for transmission.
        self.txPacketsEmitted = 0  # Number of downlink packets emitted.
        self.watchdogs = []

    def start_connection(self):
        try:
            # Set Connecting Client ID
            self.client = Client(client_id=self.client_id)
            self.client.username_pw_set(self.username, self.password)

            # call back functions
            self.client.on_connect = self.on_connect
            self.client.on_connect_fail = self.on_connect_fail
            self.client.on_publish = self.on_publish
            self.client.on_disconnect = self.on_disconnect
            self.client.on_subscribe = self.on_subscribe
            self.client.on_message = self.on_message

            print("Client connect: ", self.client.connect(self.broker, self.port, 60))
            time.sleep(1)
            self.client.loop_start()

            while not self.client.is_connected():
                print("Wait for connection")
                time.sleep(1)

            print("Client connected!")
        except BaseException as err:
            print("ERROR: Could not connect to MQTT.")
            print(f"Unexpected {err=}, {type(err)=}")
            self.close_connection()

    def conn_publish(self, state=ConnectionStateEnum.OFFLINE.name):
        conn_topic = EdgeNode.conn_topic % self.id_gateway

        # payload setting
        conn_payload = ConnPayload()
        conn_payload.state = state
        conn_payload.gatewayID = self.encoded_id_gateway

        self.publish(conn_topic, conn_payload)

    def stats_publish(self):
        stats_topic = EdgeNode.stats_topic % self.id_gateway

        # payload setting
        stats_payload = StatsPayload()
        stats_payload.gatewayID = self.encoded_id_gateway
        stats_payload.ip = self.ip
        stats_payload.time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        stats_payload.rxPacketsReceived = self.rxPacketsReceived
        stats_payload.rxPacketsReceivedOK = self.rxPacketsReceivedOK
        stats_payload.txPacketsReceived = self.txPacketsReceived
        stats_payload.txPacketsEmitted = self.txPacketsEmitted
        randstr = "stats" + str(random.randint(0, 10000)) + random.randint(0, 10000).to_bytes(4, 'big').hex()
        stats_payload.statsID = base64.b64encode(randstr.encode()).decode()

        self.publish(stats_topic, stats_payload)

    def up_link_publish(self, phy_payload):
        up_topic = EdgeNode.up_topic % self.id_gateway

        # payload setting
        randstr = str(random.randint(0, 10000)) + random.randint(0, 10000).to_bytes(4, 'big').hex()
        uplink_id = base64.b64encode(randstr.encode()).decode()
        rxInfo = RxInfo(gatewayID=self.encoded_id_gateway, time=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                        crcStatus=CRCStatusEnum.CRC_OK.name, uplinkID=uplink_id)
        up_link_payload = UpPayload(phyPayload=phy_payload, txInfo=TxInfo(), rxInfo=rxInfo)

        self.publish(up_topic, up_link_payload)

    def tack_message_publish(self, tx_ack_status, downlink_id, token):
        ack_topic = EdgeNode.ack_topic % self.id_gateway
        tx_ack_payload = TxAckPayload()
        tx_ack_payload.gatewayID = self.encoded_id_gateway
        tx_ack_payload.items.append(TxAckItemPayload(tx_ack_status.value))
        tx_ack_payload.token = token
        tx_ack_payload.downlink_id = downlink_id
        self.publish(ack_topic, tx_ack_payload)

    def publish(self, topic, payload: T):
        if not self.client.is_connected():
            return print("Client not connected")
        # json conversion
        json_payload = getJsonFromObject(payload)
        message = json.dumps(json_payload)

        result = self.client.publish(topic, message)
        status = result[0]
        if status == 0:
            print(f"Send message to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

    def subscribe(self):
        down_topic_to_sub = EdgeNode.down_topic % self.id_gateway
        self.client.subscribe(down_topic_to_sub)

    def close_connection(self):
        self.client.loop_stop()
        self.client.disconnect()

    # call back functions
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.client.connected_flag = True
            print("Connected OK Returned code=", rc)
        else:
            print("Bad connection Returned code=", rc)

    def on_connect_fail(self):
        print("connection failed")

    def on_publish(self, client, userdata, mid):
        self.txPacketsReceived += 1

    def on_disconnect(self, client, userdata, rc):
        print("client disconnected with code=", rc)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("Subscribed to topic ", mid)

    def on_message(self, client, userdata, msg):
        print(f"Edgenode `{self.id_gateway}` received message from topic: `{msg.topic}`")
        message_decoded = json.loads(msg.payload.decode())
        phyPayload = message_decoded['phyPayload']
        result = False
        for watchdog in self.watchdogs:
            result = result or watchdog.receive_message(phyPayload)

        if result:
            self.tack_message_publish(TxAckStatusEnum.OK, message_decoded['downlinkID'], message_decoded['token'])
        if msg.state == 0:
            self.rxPacketsReceivedOK += 1
        self.rxPacketsReceived += 1

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)
