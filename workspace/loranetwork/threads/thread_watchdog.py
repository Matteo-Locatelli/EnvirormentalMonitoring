import time
from threading import Thread

from enums.bcolors import BColors
from utils.api_utils import getDeviceKey


def getDecreaseBatteryLevel(timetosend, spreadingFactor, power):
    return 1 + round(20000/timetosend)


class ThreadWatchdog(Thread):
    def __init__(self, watchdog, threadLock, criticalSectionLock):
        Thread.__init__(self)
        self.watchdog = watchdog
        self.threadLock = threadLock  # serve per non accedere allo stesso gateway contemporaneamente
        self.criticalSectionLock = criticalSectionLock
        self._running = True
        self.previousMillisS = 0
        self.previousMillisR = 0
        self.previousMillisBatteryUpdate = 0
        self.timetoupdate = 2000
        self.start_time = time.time()
        self.finish_time = time.time()

    def run(self):
        resp = getDeviceKey(self.watchdog.devEUI)
        self.watchdog.app_key = resp.device_keys.nwk_key
        self.threadLock.acquire()
        self.watchdog.join()
        self.threadLock.release()
        while self._running:
            currentMillis = round(time.time() * 1000)

            if self.watchdog.batteryLevel <= 0:
                self.finish_time = time.time()
                self.stop()
                break

            if (currentMillis - self.previousMillisBatteryUpdate) > self.timetoupdate:
                spreadingFactor = None
                power = None
                self.previousMillisBatteryUpdate = currentMillis
                if self.watchdog.txInfo is not None:
                    spreadingFactor = self.watchdog.txInfo.loRaModulationInfo.spreadingFactor
                    power = self.watchdog.txInfo.power

                self.watchdog.batteryLevel -= getDecreaseBatteryLevel(self.watchdog.timetosend, spreadingFactor, power)
                self.watchdog.batteryLevel = max(self.watchdog.batteryLevel, 0)

            if (currentMillis - self.previousMillisS) > self.watchdog.timetosend:
                self.criticalSectionLock.acquire()
                self.threadLock.acquire()
                self.watchdog.send_data()
                self.threadLock.release()
                self.criticalSectionLock.release()
                self.previousMillisS = currentMillis

    def stop(self):
        self._running = False
        life_time = round((self.finish_time - self.start_time)/60, 2)
        print(f"{BColors.HEADER.value}{BColors.UNDERLINE.value}THREAD WATCHDOG {self.watchdog.deviceName} "
              f"STOPPED - LIFE TIME {life_time} minutes {BColors.ENDC.value}")
