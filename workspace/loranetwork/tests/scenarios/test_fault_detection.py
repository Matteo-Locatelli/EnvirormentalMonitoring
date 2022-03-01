"""Main module starting the application"""
import math
import random
import threading
import time
from tkinter import *

from appserver.appserver import AppServer
from enums.connection_state_enum import ConnectionStateEnum
from gui.console_log_application import ConsoleLogApplication
from nodes.edgenode import EdgeNode
from nodes.watchdog import Watchdog
from threads.thread_appserver import ThreadAppServer
from threads.thread_edgenode import ThreadEdgenode
from threads.thread_watchdog import ThreadWatchdog
from utils.api_utils import get_device_key, get_device_list, get_gateway_list

# broker address
broker = "172.28.245.217"
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
        thread_gateway.gateway.client = None


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
    app_root = Tk()
    app_root.geometry("600x600")
    app_root.resizable(True, True)
    app_root.title("Environmental monitoring")
    # app_server_app = ConsoleLogApplication(app_root, "#56D548", "green", "APP SERVER CONSOLE LOG")
    app_server = AppServer(broker=broker, port=port, id_application=application_id, ip="localhost")

    # Node list creation
    # Gateway
    # gateway_app = ConsoleLogApplication(app_root, "#128fe3", "#12c4e3", "GATEWAY CONSOLE LOG")
    gateway_list = []
    for gw in gateways:
        gateway = EdgeNode(broker=broker, port=port, id_gateway=gw.id, name=gw.name,
                           organization_id=gw.organization_id,
                           network_server_id=gw.network_server_id)
        gateway_list.append(gateway)

    # Watchdog
    # watchdog_app = ConsoleLogApplication(app_root, "#e01bd0", "#fc03f0", "WATCHDOG CONSOLE LOG")
    watchdog_list = []
    for device in devices:
        watchdog_list.append(Watchdog(application_id=device.application_id, device_name=device.name,
                                      device_profile_id=device.device_profile_id, dev_eui=device.dev_eui,
                                      battery_level_unavailable=False, battery_level=244,
                                      margin=device.device_status_margin))

    thread_watchdog_list, thread_gateway_list = assign_watchdogs_to_gateways(watchdog_list, gateway_list)
    thread_app_server = ThreadAppServer(app_server)

    # starting thread functions
    def start_threads_gateway(start_button_gateway_to_destroy, stop_call_back, button):
        gateway_window = Toplevel(app_root)
        gateway_window.geometry("900x600")
        gateway_window.title("Environmental monitoring: Gateways")

        def on_closing():
            stop_call_back(button)
            gateway_window.destroy()

        def fault(thread_gateway_to_stop, button_to_kill):
            thread_gateway_to_stop.stop()
            thread_gateway_to_stop.gateway.client = None
            button_to_kill.destroy()

        gateway_window.protocol("WM_DELETE_WINDOW", on_closing)
        gateway_app = ConsoleLogApplication(gateway_window, "#128fe3", "#12c4e3", "GATEWAY CONSOLE LOG")
        for thread_gateway in thread_gateway_list:
            thread_gateway.gateway.app = gateway_app
            thread_gateway.app = gateway_app
            thread_gateway.gateway.start_connection()
            thread_gateway.gateway.subscribe()
            thread_gateway.gateway.conn_publish(ConnectionStateEnum.ONLINE.name)
            thread_gateway.gateway.stats_publish()
            thread_gateway.start()
            button_name = f"Stop gateway {thread_gateway.gateway.id_gateway}"
            gateway_kill_button = Button(gateway_window, text=button_name)
            gateway_kill_button.config(command=lambda x=thread_gateway, y=gateway_kill_button: fault(x, y))
            gateway_kill_button.pack({"side": "left", "expand": "no", "pady": "6"})

        start_button_gateway_to_destroy.destroy()

    def stop_threads_gateway(stop_button_gateway_to_destroy):
        terminate_gateway_threads(thread_gateway_list)
        stop_button_gateway_to_destroy.destroy()

    stop_button_gateway = Button(app_root, text="Stop gateways",
                                 command=lambda: stop_threads_gateway(stop_button_gateway))
    stop_button_gateway.pack({"side": "bottom", "expand": "no"})
    start_button_gateway = Button(app_root, text="Start gateways",
                                  command=lambda: start_threads_gateway(start_button_gateway,
                                                                        stop_threads_gateway,
                                                                        stop_button_gateway))
    start_button_gateway.pack({"side": "bottom", "expand": "no"})

    def start_threads_watchdog(start_button_watchdog_to_destroy, stop_call_back, button):
        watchdog_window = Toplevel(app_root)
        watchdog_window.title("Environmental monitoring: Watchdogs")
        watchdog_window.geometry("900x600")

        def on_closing():
            stop_call_back(button)
            watchdog_window.destroy()

        watchdog_window.protocol("WM_DELETE_WINDOW", on_closing)
        watchdog_app = ConsoleLogApplication(watchdog_window, "#e01bd0", "#fc03f0", "WATCHDOG CONSOLE LOG")
        for thread_watchdog in thread_watchdog_list:
            thread_watchdog.watchdog.app = watchdog_app
            thread_watchdog.app = watchdog_app
            thread_watchdog.start()
            time.sleep(2)
        start_button_watchdog_to_destroy.destroy()

    def stop_threads_watchdog(stop_button_watchdog_to_destroy):
        terminate_watchdog_threads(thread_watchdog_list)
        stop_button_watchdog_to_destroy.destroy()

    stop_button_watchdog = Button(app_root, text="Stop watchdogs",
                                  command=lambda: stop_threads_watchdog(stop_button_watchdog))
    stop_button_watchdog.pack({"side": "left", "expand": "no"})
    start_button_watchdog = Button(app_root, text="Start watchdogs",
                                   command=lambda: start_threads_watchdog(start_button_watchdog,
                                                                          stop_threads_watchdog,
                                                                          stop_button_watchdog))
    start_button_watchdog.pack({"side": "left", "expand": "no"})

    def start_thread_app_server(start_button_to_destroy, stop_call_back, button):
        app_server_window = Toplevel(app_root)
        app_server_window.title("Environmental monitoring: App Server")
        app_server_window.geometry("900x600")

        def on_closing():
            stop_call_back(button)
            app_server_window.destroy()

        app_server_window.protocol("WM_DELETE_WINDOW", on_closing)
        app_server_app = ConsoleLogApplication(app_server_window, "#56D548", "green", "APP SERVER CONSOLE LOG")
        thread_app_server.app_server.app = app_server_app
        thread_app_server.app = app_server_app
        thread_app_server.init_app_server(devices, gateway_list)
        thread_app_server.start()
        start_button_to_destroy.destroy()

    def stop_thread_app_server(stop_button_to_destroy):
        thread_app_server.stop()
        stop_button_to_destroy.destroy()

    if app_server_enabled:
        stop_button = Button(app_root, text="Stop App Server",
                             command=lambda: stop_thread_app_server(stop_button))
        stop_button.pack({"side": "right", "expand": "no"})
        start_button = Button(app_root, text="Start App Server",
                              command=lambda: start_thread_app_server(start_button, stop_thread_app_server,
                                                                      stop_button))
        start_button.pack({"side": "right", "expand": "no"})

    app_root.mainloop()


if __name__ == "__main__":
    main()
