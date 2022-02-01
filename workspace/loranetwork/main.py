import math

from edgenode import EdgeNode
import time

from enums.connection_state_enum import ConnectionStateEnum
from utils.api_utils import getDeviceKeys
from watchdog import Watchdog

# broker address
broker = "172.30.52.14"
port = 1883

id_gateway_list = ["1f6aa45e9ed77a78"]
devices = {
    "totalCount": "1",
    "result": [
        {
            "devEUI": "0ac14aad3e6391a1",
            "name": "Device-1",
            "applicationID": "1",
            "description": "Dispositivo 1",
            "deviceProfileID": "2946f67e-54bb-4f33-a9fd-7a4d334fec19",
            "deviceProfileName": "test-chirpstack-device-profile",
            "deviceStatusBattery": 255,
            "deviceStatusMargin": 256,
            "deviceStatusExternalPowerSource": False,
            "deviceStatusBatteryLevelUnavailable": True,
            "deviceStatusBatteryLevel": 0,
            "lastSeenAt": "2022-01-30T19:27:18.797948Z"
        }
    ]
}
gateways = {
    "totalCount": "1",
    "result": [
        {
            "id": "1f6aa45e9ed77a78",
            "name": "Gateway1",
            "description": "Gateway1 nella rete",
            "createdAt": "2022-01-12T17:29:40.775382Z",
            "updatedAt": "2022-01-31T09:32:22.263418Z",
            "firstSeenAt": "2022-01-12T18:00:58.781282Z",
            "lastSeenAt": "2022-01-31T09:32:22.261376Z",
            "organizationID": "1",
            "networkServerID": "8",
            "location": {
                "latitude": 45.64721335397582,
                "longitude": 9.597843157441028,
                "altitude": 0,
                "source": "UNKNOWN",
                "accuracy": 0
            },
            "networkServerName": "test-chirpstack-network-server"
        }
    ]
}


def activate_watchdogs(watchdog_list):
    for watchdog in watchdog_list:
        resp = getDeviceKeys(watchdog.devEUI)
        watchdog.app_key = resp.device_keys.nwk_key
        watchdog.join()


def assign_watchdogs(watchdog_list, gateway_list):
    devices_per_gateway = math.ceil(len(watchdog_list) / len(gateway_list))
    i = 0
    j = 0
    while i < len(watchdog_list):
        watchdog_list[i].gateway = gateway_list[j]
        gateway_list[j].watchdogs.append(watchdog_list[i])
        i += 1
        if i >= devices_per_gateway:
            j += 1


def main():
    gateway_list = []
    gateway = EdgeNode(broker, port, id_gateway_list[0])
    gateway_list.append(gateway)
    gateway.start_connection()
    gateway.subscribe()
    gateway.conn_publish(ConnectionStateEnum.ONLINE.name)
    gateway.stats_publish()
    watchdog_list = []
    for device in devices['result']:
        watchdog_list.append(Watchdog(applicationID=device['applicationID'], deviceName=device['name'],
                                      deviceProfileID=device['deviceProfileID'], devEUI=device['devEUI'],
                                      batteryLevelUnavailable=device['deviceStatusBatteryLevelUnavailable']))
    assign_watchdogs(watchdog_list, gateway_list)
    activate_watchdogs(watchdog_list)

    for watchdog in watchdog_list:
        watchdog.send_data()

    finish = 1
    while finish != "0":
        finish = input("0 per terminare")
        time.sleep(1)

    gateway.close_connection()


if __name__ == "__main__":
    main()
