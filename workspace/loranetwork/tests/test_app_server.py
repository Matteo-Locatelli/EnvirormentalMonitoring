import time
from appserver.appserver import AppServer
from threads.thread_appserver import ThreadAppServer
from utils.api_utils import getDeviceList

broker = "172.24.167.134"
port = 1883

# configuration
applicationID = 1


def getDevices():
    limit = 100
    offset = 0
    device_list = []
    while True:
        resp = getDeviceList(applicationID, limit, offset)
        device_list.extend(resp.result)
        if resp.total_count <= (len(resp.result) + offset):
            break
        offset += len(resp.result)
    return device_list


def main():
    devices = getDevices()

    app_server = AppServer(broker=broker, port=port, id_application=applicationID, ip="localhost")
    thread_app_server = ThreadAppServer(app_server)
    thread_app_server.start(devices)
    finish = 1
    while finish != "0":
        finish = input("0 per terminare")
        time.sleep(1)

    thread_app_server.stop()


if __name__ == "__main__":
    main()
