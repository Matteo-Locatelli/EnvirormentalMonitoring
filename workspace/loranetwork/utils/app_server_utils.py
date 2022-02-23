from datetime import datetime
import base64

from enums.watchdog_battery_config_enum import WatchdogBatteryConfigEnum
from nodes.watchdog import Watchdog
from nodes.watchdog_appserver import WatchdogAppServer
from payloads.mac_layer.downlink_configuration_payload import DownlinkConfigurationPayload

MIN_TIME_TO_SEND = 1000
MIN_TIME_TO_RECEIVE = 1000


def getWatchdogAppServer(payload_msg):
    watchdog_app_server = WatchdogAppServer()
    watchdog = Watchdog(applicationID=payload_msg['applicationID'],
                        deviceName=payload_msg['deviceName'],
                        devEUI=base64.b64decode(payload_msg['devEUI'].encode()).hex(),
                        devAddr=base64.b64decode(payload_msg['devAddr'].encode()).hex())
    watchdog_app_server.watchdog = watchdog
    watchdog_app_server.last_seen = round(datetime.now().timestamp())
    print(watchdog_app_server.toJson())
    return watchdog_app_server


def getWatchdogConfiguration(watchdog_app_server):
    watchdog_configuration = DownlinkConfigurationPayload()
    battery_level_ratio = watchdog_app_server.watchdog.batteryLevel / 24
    if battery_level_ratio > 50:
        watchdog_configuration.timetosend = MIN_TIME_TO_SEND
        watchdog_configuration.timetoreceive = MIN_TIME_TO_RECEIVE
        watchdog_app_server.battery_config = WatchdogBatteryConfigEnum.NORMAL.value
    elif battery_level_ratio > 30:
        watchdog_configuration.timetosend = round(MIN_TIME_TO_SEND / 3)
        watchdog_configuration.timetoreceive = round(MIN_TIME_TO_RECEIVE / 3)
        watchdog_app_server.battery_config = WatchdogBatteryConfigEnum.SOFT_ENERGY_SAVING.value
    elif battery_level_ratio > 15:
        watchdog_configuration.timetosend = round(MIN_TIME_TO_SEND / 4)
        watchdog_configuration.timetoreceive = round(MIN_TIME_TO_RECEIVE / 4)
        watchdog_app_server.battery_config = WatchdogBatteryConfigEnum.ENERGY_SAVING_.value
    else:
        watchdog_configuration.timetosend = round(MIN_TIME_TO_SEND / 6)
        watchdog_configuration.timetoreceive = round(MIN_TIME_TO_RECEIVE / 6)
        watchdog_app_server.battery_config = WatchdogBatteryConfigEnum.HARD_ENERGY_SAVING.value

    return watchdog_configuration
