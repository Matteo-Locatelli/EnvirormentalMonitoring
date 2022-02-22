from datetime import datetime
import base64

from nodes.watchdog import Watchdog
from nodes.watchdog_appserver import WatchdogAppServer


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


