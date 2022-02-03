import time
from threading import Thread


class ThreadEdgenode(Thread):
    def __init__(self, gateway):
        Thread.__init__(self)
        self.gateway = gateway
        self._running = True

    def run(self):
        count = 0
        while self._running:
            if count % 15 == 0:
                self.gateway.stats_publish()
                count = 0
            count += 1
            time.sleep(10)

    def stop(self):
        self.gateway.close_connection()
        self._running = False
