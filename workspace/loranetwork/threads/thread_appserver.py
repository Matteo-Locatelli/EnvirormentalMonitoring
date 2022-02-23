import time
from threading import Thread

from enums.bcolors import BColors


class ThreadAppServer(Thread):
    def __init__(self, app_server):
        Thread.__init__(self)
        self._running = True
        self.app_server = app_server

    def run(self):
        while self._running:
            time.sleep(10)

    def init_app_server(self, devices):
        self.app_server.start_connection()
        for device in devices:
            self.app_server.subscribe(device.dev_eui)

    def stop(self):
        self._running = False
        self.app_server.close_connection()
        print(f"{BColors.HEADER.value}{BColors.UNDERLINE.value}THREAD APPSERVER STOPPED{BColors.ENDC.value}")
