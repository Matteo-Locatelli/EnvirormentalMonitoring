from coder import decodePhyPayload
from coder import encodePhyPayload

payloads = ["QBj/XgAACAEB1efWJyP4IQZt84BwnYItoRQB", "QBj/XgAABwEBMBBkiV4q1N23Jv5I3sAE4x3y",
            "YBj/XgCAAQAAQK1X20rG6SZsDFdeCKDMaCr4vNdaqw==", "gAQDAgEAAAAB4mTU9yQHTwA=",
            "QBj/XgAABQEBjEq4EVxLInTagRIUG7WsR5Hz"]
for payload in payloads:
    p = decodePhyPayload(payload)

    code = encodePhyPayload(p)
    print(code == payload)
