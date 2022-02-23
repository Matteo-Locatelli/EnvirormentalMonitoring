from datetime import datetime
import time
import json
import base64
from typing import TypeVar

from paho.mqtt.client import Client

from enums.bcolors import BColors
from payloads.appserver.down_command_payload import DownCommandPayload
from utils.api_utils import enqueue_device_downlink
from utils.app_server_utils import getWatchdogAppServer, getWatchdogConfiguration
from utils.payload_util import getJsonFromObject

T = TypeVar('T')


class AppServer:
    # Topics
    # Subscribe topics
    up_topic = "application/%s/device/%s/event/up"
    status_topic = "application/%s/device/%s/event/status"
    join_topic = "application/%s/device/%s/event/join"
    down_topic = "application/%s/device/%s/command/down"

    def __init__(self, broker="", port=None, id_application="", application_name="", ip="localhost",
                 network_server_id=None):
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
        self.watchdogs = dict()

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
        json_payload = getJsonFromObject(payload)
        message = json.dumps(json_payload)

        result = self.client.publish(topic, message)
        status = result[0]
        if status == 0:
            return print(f"{BColors.OKGREEN.value}AppServer send message to topic {topic}{BColors.ENDC.value}")

        return print(f"{BColors.FAIL.value}AppServer failed to send message to topic {topic}{BColors.ENDC.value}")

    def subscribe(self, devEUI):
        join_topic_to_sub = AppServer.join_topic % (self.id_application, devEUI)
        up_topic_to_sub = AppServer.up_topic % (self.id_application, devEUI)
        status_topic_to_sub = AppServer.status_topic % (self.id_application, devEUI)

        self.client.subscribe(join_topic_to_sub)
        self.client.subscribe(up_topic_to_sub)
        self.client.subscribe(status_topic_to_sub)

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
            devEUI_decoded = base64.b64decode(payload_decoded['devEUI'].encode()).hex()
            self.watchdogs[devEUI_decoded] = getWatchdogAppServer(payload_decoded)
        elif topic_type == "eventup":
            devEUI_decoded = base64.b64decode(payload_decoded['devEUI'].encode()).hex()
            self.watchdogs[devEUI_decoded].last_seen = round(datetime.now().timestamp())
            self.watchdogs[devEUI_decoded].active = True
        elif topic_type == "eventstatus":
            devEUI_decoded = base64.b64decode(payload_decoded['devEUI'].encode()).hex()
            self.watchdogs[devEUI_decoded].watchdog.batteryLevel = payload_decoded['batteryLevel']
            self.watchdogs[devEUI_decoded].watchdog.batteryLevelUnavailable = payload_decoded['batteryLevelUnavailable']
            self.watchdogs[devEUI_decoded].watchdog.margin = payload_decoded['margin']
            self.watchdogs[devEUI_decoded].last_seen = round(datetime.now().timestamp())
            if self.watchdogs[devEUI_decoded].active and not self.watchdogs[devEUI_decoded].watchdog.batteryLevelUnavailable:
                watchdog_configuration = getWatchdogConfiguration(self.watchdogs[devEUI_decoded])
                string_to_send = watchdog_configuration.toJson()
                string_to_send_encoded = base64.b64encode(string_to_send.encode()).decode()
                self.down_link_publish(devEUI_decoded, 1, False, string_to_send_encoded)
                # enqueue_device_downlink(devEUI_decoded, 1, False, string_to_send_encoded)
                device_name = self.watchdogs[devEUI_decoded].watchdog.deviceName
                print(
                    f"{BColors.OKGREEN.value}APPSERVER ENQUEQUE WATCHDOG {device_name} CONFIGURATION{BColors.ENDC.value}")

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)
