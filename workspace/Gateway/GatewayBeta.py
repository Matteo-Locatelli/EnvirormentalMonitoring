import socket
import json


UDP_IP = "localhost"
UDP_PORT = 1700
MESSAGE = "Hello, World!"

stats_payload = {
    "gatewayID": "f23ad78a721d2334",
    "ip": "172.16.209.108",
    "time": "2018-07-26T13:36:31Z",
    "location": {
        "latitude": 1.12345,
        "longitude": 2.12345,
        "altitude": 10,
        "source": "GPS",
    },
    "configVersion": "1.2.3",
    "rxPacketsReceived": 4,
    "rxPacketsReceivedOK": 1,
    "txPacketsReceived": 0,
    "txPacketsEmitted": 1
}


def run():
    MESSAGE = stats_payload
    print("UDP target IP:", UDP_IP)
    print("UDP target port:", UDP_PORT)
    print("message:", json.dumps(stats_payload))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(json.dumps(stats_payload).encode("utf-8"), (UDP_IP, UDP_PORT))


if __name__ == '__main__':
    run()
