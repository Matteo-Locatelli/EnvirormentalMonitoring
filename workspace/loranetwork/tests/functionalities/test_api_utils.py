import time
from utils.api_utils import get_device_list, get_device_key, get_gateway_list, get_last_gateway_ping

dev_eui = "0ac14aad3e6391a1"
gateway_id = "1f6aa45e9ed77a78"

print("DEVICE KEY API TEST")
resp = get_device_key(dev_eui)
print(resp)

application_id = 1
limit = 1
offset = 0
device_list = []
print("DEVICE LIST API TEST")
while True:
    resp2 = get_device_list(application_id, limit, offset)
    print(resp2)
    device_list.extend(resp2.result)
    if resp2.total_count <= (len(resp2.result) + offset):
        break

    offset += len(resp2.result)

print(type(device_list[0].device_profile_id))
print("**")
print(device_list[1])

print("GATEWAY LIST API TEST")
print(get_gateway_list(limit, offset))

print("GATEWAY PING API TEST")
count = 0
while count < 10:
    ping = get_last_gateway_ping(gateway_id)
    print("Ping")
    print(ping)
    count += 1
    time.sleep(10)

