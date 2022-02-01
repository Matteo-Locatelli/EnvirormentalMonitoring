def manageJoinAcceptRequest(gateway, phyPayload):
    found = False
    for w in gateway.watchdogs:
        w.activate(phyPayload)

    return found
