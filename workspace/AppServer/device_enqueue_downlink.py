import grpc
from chirpstack_api.as_pb.external import api

# Configuration.

server = "localhost:8080"

# Va genera dall'interfaccia grafica (api keys)
api_token = ""

def device_enqueque_downlink(data, dev_eui):
    channel = grpc.insecure_channel(server)

    # Device-queue API client
    client = api.DeviceQueueServiceStub(channel)

    auth_token = [("authorization", "Bearer %s" % api_token)]

    # Construct request
    req = api.EnqueueDeviceQueueItemRequest()
    req.device_queue_item.confirmed = False
    req.device_queue_item.data = bytes(data)
    req.device_queue_item.dev_eui = bytes(dev_eui).hex()
    req.device_queue_item.f_port = 10

    resp = client.Enqueue(req, metadata=auth_token)

    print(resp)
