import grpc
from chirpstack_api.as_pb.external import api

# This must point to the API interface.
server = "localhost:8080"

# The API token
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlfa2V5X2lkIjoiNTFmNWVhMmItZGVkOC00ZjU2LTlkOGYtMTU0YTIwYjZiMDZmIiwiYXVkIjoiYXMiLCJpc3MiOiJhcyIsIm5iZiI6MTY0Mjg3MDU4Miwic3ViIjoiYXBpX2tleSJ9.cCLELlxRPbSk8YFJm4ndjxjssmAX4BKEizDKVp3TWpo"


def getDeviceList(applicationID, limit, offset):
    channel = grpc.insecure_channel(server)

    client = api.DeviceServiceStub(channel)

    auth_token = [("authorization", "Bearer %s" % api_token)]

    # Construct request.
    req = api.ListDeviceRequest()
    req.application_id = applicationID
    req.limit = limit
    req.offset = offset
    resp = client.List(req, metadata=auth_token)
    return resp


def getGatewayList(limit, offset):
    channel = grpc.insecure_channel(server)

    client = api.GatewayServiceStub(channel)

    auth_token = [("authorization", "Bearer %s" % api_token)]

    # Construct request.
    req = api.ListGatewayRequest()
    req.limit = limit
    req.offset = offset
    resp = client.List(req, metadata=auth_token)
    return resp


def getDeviceKey(dev_eui):
    channel = grpc.insecure_channel(server)

    client = api.DeviceServiceStub(channel)

    auth_token = [("authorization", "Bearer %s" % api_token)]

    # Construct request.
    req = api.DeviceKeys()
    req.dev_eui = dev_eui
    resp = client.GetKeys(req, metadata=auth_token)
    return resp


def enqueue_device_downlink(dev_eui, fPort, confirmed, data):
    channel = grpc.insecure_channel(server)

    # Device-queue API client.
    client = api.DeviceQueueServiceStub(channel)

    auth_token = [("authorization", "Bearer %s" % api_token)]

    dev_eui_hex = int(dev_eui, 16).to_bytes(8, 'big').hex()
    # Construct request.
    req = api.EnqueueDeviceQueueItemRequest()
    req.device_queue_item.confirmed = confirmed
    req.device_queue_item.data = bytes(data.encode())
    req.device_queue_item.dev_eui = dev_eui_hex
    req.device_queue_item.f_port = fPort

    resp = client.Enqueue(req, metadata=auth_token)

    # Print the downlink frame-counter value.
    print(resp.f_cnt)
