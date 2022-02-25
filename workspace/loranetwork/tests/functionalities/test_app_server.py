import time
from appserver.appserver import AppServer
from enums.connection_state_enum import ConnectionStateEnum
from nodes.edgenode import EdgeNode
from threads.thread_appserver import ThreadAppServer
from utils.api_utils import get_device_list, get_gateway_list

broker = "172.30.220.135"
port = 1883

# configuration
application_id = 1


def get_gateways():
    limit = 100
    offset = 0
    gateway_list = []
    while True:
        resp = get_gateway_list(limit, offset)
        gateway_list.extend(resp.result)
        if resp.total_count <= (len(resp.result) + offset):
            break
        offset += len(resp.result)
    return gateway_list


def get_devices():
    limit = 100
    offset = 0
    device_list = []
    while True:
        resp = get_device_list(application_id, limit, offset)
        device_list.extend(resp.result)
        if resp.total_count <= (len(resp.result) + offset):
            break
        offset += len(resp.result)
    return device_list


def main():
    devices = get_devices()
    gateways = get_gateways()

    gateway_list = []
    for gw in gateways:
        gateway = EdgeNode(broker=broker, port=port, id_gateway=gw.id, name=gw.name,
                           organization_id=gw.organization_id,
                           network_server_id=gw.network_server_id)
        # gateway.start_connection()
        # gateway.subscribe()
        # gateway.conn_publish(ConnectionStateEnum.ONLINE.name)
        # gateway.stats_publish()
        # time.sleep(1)
        gateway_list.append(gateway)

    app_server = AppServer(broker=broker, port=port, id_application=application_id, ip="localhost")
    thread_app_server = ThreadAppServer(app_server)
    thread_app_server.init_app_server(devices, gateway_list)
    thread_app_server.start()
    finish = 1
    while finish != "0":
        finish = input("0 per terminare")
        time.sleep(1)

    thread_app_server.stop()


if __name__ == "__main__":
    main()
