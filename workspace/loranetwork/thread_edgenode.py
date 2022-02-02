from threading import Thread
import time


class ThreadEdgenode(Thread):
    def __init__(self, gateway):
        Thread.__init__(self)
        self.gateway = gateway

    def run(self):
        count = 0
        while True:
            if count % 15 == 0:
                self.gateway.stats_publish()
                count = 0
            count += 1
            time.sleep(1)
