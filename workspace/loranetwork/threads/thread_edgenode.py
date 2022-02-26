import time
from threading import Thread

from enums.bcolors import BColors


class ThreadEdgenode(Thread):
    def __init__(self, gateway, gateway_app=None):
        Thread.__init__(self)
        self.gateway = gateway
        self._running = True
        self.app = gateway_app

    def run(self):
        count = 0
        while self._running:
            if count % 15 == 0:
                self.gateway.stats_publish()
                count = 0
            count += 1
            time.sleep(10)

    def stop(self):
        if self._running:
            self._running = False
            self.gateway.close_connection()
            print(f"{BColors.OKCYAN.value}{BColors.UNDERLINE.value}THREAD EDGENODE {self.gateway.id_gateway} STOPPED{BColors.ENDC.value}")
