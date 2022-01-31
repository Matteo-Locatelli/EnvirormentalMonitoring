from edgenode import EdgeNode
import time

from enums.connection_state_enum import ConnectionStateEnum

# broker address
broker = "172.30.33.54"
port = 1883

appKey = "a772a9b9c627b3a41370b8a8646e6e80"
appSKey = "880d2a5d7869a9e2f26989a1ab66548d"

id_gateway_list = ["f23ad78a721d2334"]
devStatus = {
    "totalCount": "1",
    "result": [
        {
            "devEUI": "0ac14aad3e6391a1",
            "name": "Device-1",
            "applicationID": "1",
            "description": "Dispositivo 1",
            "deviceProfileID": "2946f67e-54bb-4f33-a9fd-7a4d334fec19",
            "deviceProfileName": "test-chirpstack-device-profile",
            "deviceStatusBattery": 255,
            "deviceStatusMargin": 256,
            "deviceStatusExternalPowerSource": False,
            "deviceStatusBatteryLevelUnavailable": True,
            "deviceStatusBatteryLevel": 0,
            "lastSeenAt": "2022-01-30T19:27:18.797948Z"
        }
    ]
}
gateway = EdgeNode(broker, port, id_gateway_list[0])
try:
    gateway.start_connection()
    gateway.conn_publish(ConnectionStateEnum.ONLINE.name)
    gateway.stats_publish()
    time.sleep(1)
except BaseException as err:
    gateway.close_connection()
    print("Something went wrong!")
    print("Error: ", str(err))
