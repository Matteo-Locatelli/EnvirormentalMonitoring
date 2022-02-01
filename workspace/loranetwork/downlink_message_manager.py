
def manageJoinAcceptRequest(gateway, phyPayload):
    watchdog = None
    for w in gateway.watchdogs:
        if w.devEUI == phyPayload.macPayload.devEUI and w.joinEUI == phyPayload.macPayload.joinEUI:
            watchdog = w
            break
    watchdog.activate(phyPayload)
    return None