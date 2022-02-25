"""Main module starting the application"""
import math
import random
import threading
import time

from appserver.appserver import AppServer
from enums.connection_state_enum import ConnectionStateEnum
from nodes.edgenode import EdgeNode
from nodes.watchdog import Watchdog
from threads.thread_appserver import ThreadAppServer
from threads.thread_edgenode import ThreadEdgenode
from threads.thread_watchdog import ThreadWatchdog
from utils.api_utils import get_device_key, get_device_list, get_gateway_list

# broker address
broker = "172.30.220.135"
port = 1883

# configuration
application_id = 1
app_server_enabled = True


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


def activate_watchdogs(watchdog_list):
    for watchdog in watchdog_list:
        resp = get_device_key(watchdog.devEUI)
        watchdog.app_key = resp.device_keys.nwk_key
        watchdog.join()


def assign_watchdogs_to_gateways(watchdog_list, gateway_list):
    devices_per_gateway = math.ceil(len(watchdog_list) / len(gateway_list))
    thread_watchdog_list = []
    thread_gateway_list = []

    i = 0
    j = 0
    thread_lock = threading.Lock()
    while i < len(watchdog_list):
        if i % devices_per_gateway == 0 and i > 0:
            thread_lock = threading.Lock()
            j += 1
        critical_section_lock = threading.Lock()
        thread_watchdog = ThreadWatchdog(watchdog_list[i], thread_lock, critical_section_lock)
        thread_edgenode = ThreadEdgenode(gateway_list[j])

        watchdog_list[i].gateways.append(gateway_list[j])
        gateway_list[j].watchdogs.append(watchdog_list[i])

        thread_gateway_list.append(thread_edgenode)
        thread_watchdog_list.append(thread_watchdog)
        i += 1

    return thread_watchdog_list, thread_gateway_list


def assign_watchdogs_to_gateways_full_connected(watchdog_list, gateway_list):
    devices_per_gateway = math.ceil(len(watchdog_list) / len(gateway_list))
    thread_watchdog_list = []
    thread_gateway_list = []

    first = True
    for gateway in gateway_list:
        thread_lock = threading.Lock()
        thread_edgenode = ThreadEdgenode(gateway)
        for watchdog in watchdog_list:
            if first:
                critical_section_lock = threading.Lock()
                thread_watchdog = ThreadWatchdog(watchdog, thread_lock, critical_section_lock)
                thread_watchdog_list.append(thread_watchdog)

            watchdog.gateways.append(gateway)
            gateway.watchdogs.append(watchdog)

        first = False
        thread_gateway_list.append(thread_edgenode)
    return thread_watchdog_list, thread_gateway_list


def terminate_gateway_threads(thread_gateway_list):
    for thread_gateway in thread_gateway_list:
        thread_gateway.stop()


def terminate_watchdog_threads(thread_watchdog_list):
    for thread_watchdog in thread_watchdog_list:
        thread_watchdog.criticalSectionLock.acquire()
        thread_watchdog.stop()
        thread_watchdog.criticalSectionLock.release()


def main():
    # get nodes
    devices = get_devices()
    gateways = get_gateways()

    # App Server
    app_server = AppServer(broker=broker, port=port, id_application=application_id, ip="localhost")

    # Node list creation
    gateway_list = []
    for gw in gateways:
        gateway = EdgeNode(broker=broker, port=port, id_gateway=gw.id, name=gw.name,
                           organization_id=gw.organization_id,
                           network_server_id=gw.network_server_id)
        gateway.start_connection()
        gateway.subscribe()
        gateway.conn_publish(ConnectionStateEnum.ONLINE.name)
        gateway.stats_publish()
        time.sleep(1)
        gateway_list.append(gateway)

    watchdog_list = []
    for device in devices:
        watchdog_list.append(Watchdog(application_id=device.application_id, device_name=device.name,
                                      device_profile_id=device.device_profile_id, dev_eui=device.dev_eui,
                                      battery_level_unavailable=False,
                                      battery_level=244, margin=device.device_status_margin))

    thread_watchdog_list, thread_gateway_list = assign_watchdogs_to_gateways_full_connected(watchdog_list, gateway_list)
    thread_app_server = ThreadAppServer(app_server)

    # starting threads
    for thread_gateway in thread_gateway_list:
        thread_gateway.start()
    for thread_watchdog in thread_watchdog_list:
        thread_watchdog.start()
        time.sleep(2)

    if app_server_enabled:
        thread_app_server.init_app_server(devices, gateway_list)
        thread_app_server.start()

    # Fault simulation
    time.sleep(10)
    max_index = len(thread_gateway_list) - 1
    thread_gateway_list[random.randint(0, max_index)].stop()

    finish = 1
    while finish != "0":
        finish = input("0 per terminare")
        time.sleep(5)

    terminate_gateway_threads(thread_gateway_list)
    terminate_watchdog_threads(thread_watchdog_list)

    if app_server_enabled:
        thread_app_server.stop()


if __name__ == "__main__":
    main()
