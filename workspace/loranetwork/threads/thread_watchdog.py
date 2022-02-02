from threading import Thread
import time

from utils.api_utils import getDeviceKeys


class ThreadWatchdog(Thread):
    def __init__(self, watchdog, threadLock):
        Thread.__init__(self)
        self.watchdog = watchdog
        self.threadLock = threadLock #serve per non accedere allo stesso gateway contemporaneamente

    def run(self):
        resp = getDeviceKeys(self.watchdog.devEUI)
        self.watchdog.app_key = resp.device_keys.nwk_key
        self.threadLock.acquire()
        self.watchdog.join()
        self.threadLock.release()
        while True:
            currentMillis = round(time.time() * 1000)
            if (currentMillis - self.watchdog.previousMillisS) > self.watchdog.timetosend:
                self.watchdog.send_data()
                self.watchdog.previousMillisS = currentMillis



