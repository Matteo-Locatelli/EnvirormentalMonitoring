from edgenode import EdgeNode
import time

from enums.connection_state_enum import ConnectionStateEnum

# broker adress
broker = "172.30.33.54"
port = 1883;

id_gateway_list = ["f23ad78a721d2334"]

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
