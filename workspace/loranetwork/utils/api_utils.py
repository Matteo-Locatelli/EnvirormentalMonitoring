import grpc
from chirpstack_api.as_pb.external import api

# This must point to the API interface.
server = "localhost:8080"

# The API token
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlfa2V5X2lkIjoiNTFmNWVhMmItZGVkOC00ZjU2LTlkOGYtMTU0YTIwYjZiMDZmIiwiYXVkIjoiYXMiLCJpc3MiOiJhcyIsIm5iZiI6MTY0Mjg3MDU4Miwic3ViIjoiYXBpX2tleSJ9.cCLELlxRPbSk8YFJm4ndjxjssmAX4BKEizDKVp3TWpo"


def getDeviceList(applicationID, limit, offset):
    # Connect without using TLS.
    channel = grpc.insecure_channel(server)

    # Device-queue API client.
    client = api.DeviceServiceStub(channel)

    # Define the API key meta-data.
    auth_token = [("authorization", "Bearer %s" % api_token)]

    # Construct request.
    req = api.ListDeviceRequest()
    req.application_id = applicationID
    req.limit = limit
    req.offset = offset
    resp = client.List(req, metadata=auth_token)
    return resp


def getGatewayList(limit, offset):
    # Connect without using TLS.
    channel = grpc.insecure_channel(server)

    # Device-queue API client.
    client = api.GatewayServiceStub(channel)

    # Define the API key meta-data.
    auth_token = [("authorization", "Bearer %s" % api_token)]

    # Construct request.
    req = api.ListGatewayRequest()
    req.limit = limit
    req.offset = offset
    resp = client.List(req, metadata=auth_token)
    return resp


def getDeviceKeys(dev_eui):
    # Connect without using TLS.
    channel = grpc.insecure_channel(server)

    # Device-queue API client.
    client = api.DeviceServiceStub(channel)

    # Define the API key meta-data.
    auth_token = [("authorization", "Bearer %s" % api_token)]

    # Construct request.
    req = api.DeviceKeys()
    req.dev_eui = dev_eui
    resp = client.GetKeys(req, metadata=auth_token)
    return resp
