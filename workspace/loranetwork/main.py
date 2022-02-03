import math
import threading
import time

from enums.connection_state_enum import ConnectionStateEnum
from nodes.edgenode import EdgeNode
from nodes.watchdog import Watchdog
from threads.thread_edgenode import ThreadEdgenode
from threads.thread_watchdog import ThreadWatchdog
from utils.api_utils import getDeviceKeys, getDeviceList, getGatewayList

# broker address
broker = "172.18.200.139"
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
        else:
            offset += len(resp.result)
    return device_list


def getGateways():
    limit = 100
    offset = 0
    gateway_list = []
    while True:
        resp = getGatewayList(limit, offset)
        gateway_list.extend(resp.result)
        if resp.total_count <= (len(resp.result) + offset):
            break
        else:
            offset += len(resp.result)
    return gateway_list


def activate_watchdogs(watchdog_list):
    for watchdog in watchdog_list:
        resp = getDeviceKeys(watchdog.devEUI)
        watchdog.app_key = resp.device_keys.nwk_key
        watchdog.join()


def assign_watchdogs_to_gateways(watchdog_list, gateway_list):
    devices_per_gateway = math.ceil(len(watchdog_list) / len(gateway_list))
    thread_watchdog_list = []
    thread_gateway_list = []

    i = 0
    j = 0
    threadLock = threading.Lock()
    while i < len(watchdog_list):
        if i % devices_per_gateway == 0 and i > 0:
            threadLock = threading.Lock()
            j += 1
        criticalSectionLock = threading.Lock()
        thread_watchdog = ThreadWatchdog(watchdog_list[i], threadLock, criticalSectionLock)
        thread_edgenode = ThreadEdgenode(gateway_list[j])

        watchdog_list[i].gateway = gateway_list[j]
        gateway_list[j].watchdogs.append(watchdog_list[i])

        thread_gateway_list.append(thread_edgenode)
        thread_watchdog_list.append(thread_watchdog)
        i += 1

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
    devices = getDevices()
    gateways = getGateways()

    # list creation
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
        watchdog_list.append(Watchdog(applicationID=device.application_id, deviceName=device.name,
                                      deviceProfileID=device.device_profile_id, devEUI=device.dev_eui,
                                      batteryLevelUnavailable=device.device_status_battery_level_unavailable,
                                      batteryLevel=device.device_status_battery, margin=device.device_status_margin))

    thread_watchdog_list, thread_gateway_list = assign_watchdogs_to_gateways(watchdog_list, gateway_list)

    # starting threads
    for thread_gateway in thread_gateway_list:
        thread_gateway.start()
    for thread_watchdog in thread_watchdog_list:
        thread_watchdog.start()

    time.sleep(1)

    finish = 1
    while finish != "0":
        finish = input("0 per terminare")
        time.sleep(1)

    terminate_gateway_threads(thread_gateway_list)
    terminate_watchdog_threads(thread_watchdog_list)


if __name__ == "__main__":
    main()
