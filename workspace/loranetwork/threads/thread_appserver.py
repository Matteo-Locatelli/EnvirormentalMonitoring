import time
from threading import Thread

from appserver.gateway_appserver import GatewayAppServer
from enums.bcolors import BColors
from nodes.edgenode import EdgeNode


class ThreadAppServer(Thread):
    def __init__(self, app_server):
        Thread.__init__(self)
        self._running = True
        self.app_server = app_server
        self.time_to_check = 10000
        self.previousMillsCheck = 0

    def run(self):
        while self._running:
            current_millis = round(time.time() * 1000)
            if (current_millis - self.previousMillsCheck) > self.time_to_check:
                self.app_server.check_nodes()
                self.previousMillsCheck = current_millis

    def init_app_server(self, devices=[], gateways=[]):
        self.app_server.start_connection()
        for device in devices:
            self.app_server.subscribe(device.dev_eui)
        for gateway in gateways:
            gateway_app_server = GatewayAppServer()
            gateway_app_server.gateway = gateway
            gateway_app_server.last_seen = 0
            gateway_app_server.active = True
            self.app_server.gateways[gateway.id_gateway] = gateway_app_server
            self.app_server.subscribe_ping(gateway.id_gateway)

    def stop(self):
        self._running = False
        self.app_server.close_connection()
        print(f"{BColors.OKGREEN.value}{BColors.UNDERLINE.value}THREAD APPSERVER STOPPED{BColors.ENDC.value}")
