from threading import Thread
import time

from utils.api_utils import getDeviceKeys


class ThreadWatchdog(Thread):
    def __init__(self, watchdog):
        Thread.__init__(self)
        self.watchdog = watchdog

    def run(self):
        resp = getDeviceKeys(self.watchdog.devEUI)
        self.watchdog.app_key = resp.device_keys.nwk_key
        self.watchdog.join()
