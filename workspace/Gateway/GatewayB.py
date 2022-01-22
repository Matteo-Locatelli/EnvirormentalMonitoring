import os
import sys

import grpc
from chirpstack_api.as_pb.external import api

# Configuration.

# This must point to the API interface.
server = "localhost:8080"

# The DevEUI for which you want to enqueue the downlink.

dev_eui = bytes([0x0a, 0xc1, 0x4a, 0xad, 0x3e, 0x63, 0x91, 0xa1])

# The API token (retrieved using the web-interface).
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlfa2V5X2lkIjoiNTFmNWVhMmItZGVkOC00ZjU2LTlkOGYtMTU0YTIwYjZiMDZmIiwiYXVkIjoiYXMiLCJpc3MiOiJhcyIsIm5iZiI6MTY0Mjg3MDU4Miwic3ViIjoiYXBpX2tleSJ9.cCLELlxRPbSk8YFJm4ndjxjssmAX4BKEizDKVp3TWpo"

if __name__ == "__main__":
  # Connect without using TLS.
  channel = grpc.insecure_channel(server)

  # Device-queue API client.
  client = api.DeviceQueueServiceStub(channel)

  # Define the API key meta-data.
  auth_token = [("authorization", "Bearer %s" % api_token)]

  # Construct request.
  req = api.EnqueueDeviceQueueItemRequest()
  req.device_queue_item.confirmed = False
  req.device_queue_item.data = bytes([0x01, 0x02, 0x03])
  req.device_queue_item.dev_eui = dev_eui.hex()
  req.device_queue_item.f_port = 1

  resp = client.Enqueue(req, metadata=auth_token)

  # Print the downlink frame-counter value.
  print(resp)