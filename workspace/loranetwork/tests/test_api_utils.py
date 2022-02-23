from utils.api_utils import get_device_list, get_device_key, get_gateway_list

dev_eui = "0ac14aad3e6391a1"
resp = get_device_key(dev_eui)
print(resp)

application_id = 1
limit = 1
offset = 0
device_list = []
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

print(get_gateway_list(limit, offset))
