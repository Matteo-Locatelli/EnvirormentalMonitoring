import socket
import json
from random import randint

UDP_IP = "172.21.185.160"
UDP_PORT = 1700
MESSAGE = "Hello, World!"

stats_payload = {
  "gatewayID": "H2qkXp7Xeng=",
  "ip": "172.21.185.160",
  "time": "2022-01-27T20:12:23Z",
  "location": None,
  "configVersion": "",
  "rxPacketsReceived": 2,
  "rxPacketsReceivedOK": 0,
  "txPacketsReceived": 3,
  "txPacketsEmitted": 0,
  "metaData": {},
  "statsID": "JCjPH3lARfGInuGpcdn1jA==",
  "txPacketsPerFrequency": {},
  "rxPacketsPerFrequency": {},
  "txPacketsPerModulation": [],
  "rxPacketsPerModulation": [],
  "txPacketsPerStatus": {}
}

p_version = 2;
RandomToken = "Random"
IpAdrr = "172.16.209.108"


def run():
    MESSAGE = stats_payload
    print("UDP target IP:", UDP_IP)
    print("UDP target port:", UDP_PORT)
    print("message:", json.dumps(stats_payload))

    packet = bytearray()
    packet.append(p_version)
    packet.append(randint(0, 100))  # Random token
    packet.append(randint(0, 100))
    packet.append(3)                # Data identifier
    packet.append(172)              # Address
    packet.append(16)
    packet.append(209)
    packet.append(108)
    packet.append(0)
    print(packet)
    # binary.LittleEndian.PutUint16(out[1:3], p.RandomToken)
    # out[3] = byte(PushData)
    # out = append(out, p.GatewayMAC[0:len(p.GatewayMAC)]...)
    # out = append(out, pb...)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(packet, (UDP_IP, UDP_PORT))


if __name__ == '__main__':
    run()
