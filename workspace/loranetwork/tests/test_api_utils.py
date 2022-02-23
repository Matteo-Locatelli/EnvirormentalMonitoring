from utils.api_utils import getDeviceList, getDeviceKey, getGatewayList

devEUI = "0ac14aad3e6391a1"
resp = getDeviceKey(devEUI)
print(resp)

applicationID = 1
limit = 1
offset = 0
device_list = []
while True:
    resp2 = getDeviceList(applicationID, limit, offset)
    print(resp2)
    device_list.extend(resp2.result)
    if resp2.total_count <= (len(resp2.result) + offset):
        break

    offset += len(resp2.result)

print(type(device_list[0].device_profile_id))
print("**")
print(device_list[1])

print(getGatewayList(limit, offset))
