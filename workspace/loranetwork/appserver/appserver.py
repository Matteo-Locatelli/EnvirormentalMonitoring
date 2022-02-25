from datetime import datetime
import time
import json
import base64
import random
from typing import TypeVar

from paho.mqtt.client import Client

from enums.bcolors import BColors
from enums.working_state_enum import WorkingStateEnum
from payloads.appserver.down_command_payload import DownCommandPayload
from payloads.appserver.ping_payload import PingPayload
from utils.app_server_utils import get_watchdog_app_server, get_watchdog_configuration
from utils.payload_util import get_json_from_object

T = TypeVar('T')


class AppServer:
    # Topics
    # Subscribe topics
    up_topic = "application/%s/device/%s/event/up"
    status_topic = "application/%s/device/%s/event/status"
    join_topic = "application/%s/device/%s/event/join"
    down_topic = "application/%s/device/%s/command/down"
    ping_topic = "gateway/%s/command/ping"
    echo_topic = "gateway/%s/event/echo"

    # Timeout
    watchdog_timeout = 10000
    gateway_timout = 20000

    def __init__(self, broker="", port=None, id_application="", application_name="", ip="localhost"):
        self.broker = broker
        self.port = port
        self.ip = ip
        self.client = None
        self.client_id = "loraappserver" + str(id_application)
        self.username = "chirpstack_as"
        self.password = ""
        self.id_application = id_application
        self.application_name = application_name
        self.can_sand_data = False
        self.watchdogs = {}
        self.gateways = {}

    def start_connection(self):
        try:
            # Set Connecting Client ID
            self.client = Client(client_id=self.client_id)
            self.client.username_pw_set(self.username, self.password)

            # call back functions
            self.client.on_connect = self.on_connect
            self.client.on_connect_fail = self.on_connect_fail
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message

            print(f"{BColors.OKGREEN.value}AppServer "
                  f"connect: {self.client.connect(self.broker, self.port, 60)} {BColors.ENDC.value}")
            time.sleep(1)
            self.client.loop_start()

            while not self.client.is_connected():
                time.sleep(1)

            print(f"{BColors.OKGREEN.value}AppServer connected!{BColors.ENDC.value}")
        except BaseException as err:
            print(f"{BColors.WARNING.value}ERROR: AppServer Could not connect to MQTT.{BColors.ENDC.value}")
            print(f"{BColors.FAIL.value}Unexpected {err=}, {type(err)=}{BColors.ENDC.value}")
            self.close_connection()

    def down_link_publish(self, dev_eui, port, confirmed, data):
        down_topic = AppServer.down_topic % (self.id_application, dev_eui)
        down_command_payload = DownCommandPayload()
        down_command_payload.fPort = port
        down_command_payload.confirmed = confirmed
        down_command_payload.data = data
        self.publish(down_topic, down_command_payload)

    def publish(self, topic, payload: T):
        if not self.client.is_connected():
            return print(f"{BColors.WARNING.value}Appserver not connected{BColors.ENDC.value}")
        # json conversion
        json_payload = get_json_from_object(payload)
        message = json.dumps(json_payload)

        result = self.client.publish(topic, message)
        status = result[0]
        if status == 0:
            return print(f"{BColors.OKGREEN.value}AppServer send message to topic {topic}{BColors.ENDC.value}")

        return print(f"{BColors.FAIL.value}AppServer failed to send message to topic {topic}{BColors.ENDC.value}")

    def subscribe(self, dev_eui):
        join_topic_to_sub = AppServer.join_topic % (self.id_application, dev_eui)
        up_topic_to_sub = AppServer.up_topic % (self.id_application, dev_eui)
        status_topic_to_sub = AppServer.status_topic % (self.id_application, dev_eui)

        self.client.subscribe(join_topic_to_sub)
        self.client.subscribe(up_topic_to_sub)
        self.client.subscribe(status_topic_to_sub)

    def subscribe_ping(self, gateway_id):
        echo_topic_to_sub = AppServer.echo_topic % gateway_id
        self.client.subscribe(echo_topic_to_sub)

    def ping_gateway(self, gateway_id):
        ping_topic = AppServer.ping_topic % gateway_id
        ping_payload = PingPayload()
        ping_payload.gateway_id = gateway_id
        randstr = "ping" + str(random.randint(0, 10000)) + random.randint(0, 10000).to_bytes(4, 'big').hex()
        ping_payload.ping_id = base64.b64encode(randstr.encode()).decode()
        self.publish(ping_topic, ping_payload)
        self.gateways[gateway_id].num_pending_pings += 1
        print(f"{BColors.OKGREEN.value}PING EDGENODE {gateway_id}{BColors.ENDC.value}")

    def check_nodes(self):
        current_timestamp = round(datetime.now().timestamp())
        for dev_eui in self.watchdogs:
            interval_time = (current_timestamp - self.watchdogs[dev_eui].last_seen) * 1000
            if interval_time > AppServer.watchdog_timeout and self.watchdogs[dev_eui].active:
                self.watchdogs[dev_eui].num_failure += 1
            if self.watchdogs[dev_eui].num_failure >= 3 and self.watchdogs[dev_eui].active:
                self.watchdogs[dev_eui].state = WorkingStateEnum.KO.name
                self.watchdogs[dev_eui].active = False
                print(f"{BColors.WARNING.value}WATCHDOG {dev_eui} IS SILENT{BColors.ENDC.value}")
        for gateway_id in self.gateways:
            interval_time = (current_timestamp - self.gateways[gateway_id].last_seen) * 1000
            if interval_time > AppServer.gateway_timout and self.gateways[gateway_id].active:
                self.ping_gateway(gateway_id)
            if self.gateways[gateway_id].num_pending_pings >= 3 and self.gateways[gateway_id].active:
                self.gateways[gateway_id].state = WorkingStateEnum.KO.name
                self.gateways[gateway_id].active = False
                print(f"{BColors.WARNING.value}EDGENODE {gateway_id} IS NOT WORKING{BColors.ENDC.value}")

    def close_connection(self):
        self.client.loop_stop()
        self.client.disconnect()

    # call back functions
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.client.connected_flag = True
            print(f"{BColors.OKGREEN.value}Connected OK Returned code={rc}{BColors.ENDC.value}")
        else:
            print(f"{BColors.FAIL.value}Bad connection Returned code={rc}{BColors.ENDC.value}")

    def on_connect_fail(self):
        print(f"{BColors.FAIL.value}AppServer connection failed{BColors.ENDC.value}")

    def on_disconnect(self, client, userdata, rc):
        print(f"{BColors.OKGREEN.value}AppServer disconnected with code={rc}{BColors.ENDC.value}")

    def on_message(self, client, userdata, msg):
        print(f"{BColors.OKGREEN.value}AppServer received message from topic: {msg.topic}{BColors.ENDC.value}")
        topic_splitted = msg.topic.split("/")
        topic_type = topic_splitted[-2] + topic_splitted[-1]
        payload_decoded = json.loads(msg.payload.decode())
        if topic_type == "eventjoin":
            dev_eui_decoded = base64.b64decode(payload_decoded['devEUI'].encode()).hex()
            self.watchdogs[dev_eui_decoded] = get_watchdog_app_server(payload_decoded)
        elif topic_type == "eventup":
            dev_eui_decoded = base64.b64decode(payload_decoded['devEUI'].encode()).hex()
            self.watchdogs[dev_eui_decoded].last_seen = round(datetime.now().timestamp())
            self.watchdogs[dev_eui_decoded].active = True
        elif topic_type == "eventstatus":
            dev_eui_decoded = base64.b64decode(payload_decoded['devEUI'].encode()).hex()
            self.watchdogs[dev_eui_decoded].watchdog.batteryLevel = payload_decoded['batteryLevel']
            self.watchdogs[dev_eui_decoded].watchdog.batteryLevelUnavailable = payload_decoded[
                'batteryLevelUnavailable']
            self.watchdogs[dev_eui_decoded].watchdog.margin = payload_decoded['margin']
            self.watchdogs[dev_eui_decoded].last_seen = round(datetime.now().timestamp())
            if self.watchdogs[dev_eui_decoded].active and \
                    not self.watchdogs[dev_eui_decoded].watchdog.batteryLevelUnavailable:
                watchdog_configuration = get_watchdog_configuration(self.watchdogs[dev_eui_decoded])
                string_to_send = watchdog_configuration.to_json()
                string_to_send_encoded = base64.b64encode(string_to_send.encode()).decode()
                self.down_link_publish(dev_eui_decoded, 1, False, string_to_send_encoded)
                # enqueue_device_downlink(devEUI_decoded, 1, False, string_to_send_encoded)
                device_name = self.watchdogs[dev_eui_decoded].watchdog.deviceName
                print(
                    f"{BColors.OKGREEN.value}APPSERVER ENQUEQUE WATCHDOG {device_name} CONFIGURATION{BColors.ENDC.value}")
        elif topic_type == "eventecho":
            self.gateways[payload_decoded['gateway_id']].last_seen = round(datetime.now().timestamp())
            self.gateways[payload_decoded['gateway_id']].num_pending_pings = 0
            self.gateways[payload_decoded['gateway_id']].state = WorkingStateEnum.OK.name
            self.gateways[payload_decoded['gateway_id']].active = True

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)
