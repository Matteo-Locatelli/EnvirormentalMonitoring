import time
from threading import Thread


class ThreadAppServer(Thread):
    def __init__(self, app_server):
        Thread.__init__(self)
        self._running = True
        self.app_server = app_server

    def run(self):
        while self._running:
            time.sleep(10)

    def start(self, devices):
        self.app_server.start_connection()
        for device in devices:
            self.app_server.subscribe(device.dev_eui)

    def stop(self):
        self._running = False
        self.app_server.close_connection()
        print("thread_appserver stopped")
