import json


class JoinAccpetMacPayload:
    def __init__(self, app_nonce=None, net_ID=None, dev_addr=None, DL_settings=None, rx_delay=None, CF_list=None,
                 nwk_SKey=None, app_SKey=""):
        self.app_nonce = app_nonce
        self.net_ID = net_ID
        self.dev_addr = dev_addr
        self.DL_settings = DL_settings
        self.rx_delay = rx_delay
        self.CF_list = CF_list
        self.nwk_SKey = nwk_SKey
        self.app_SKey = app_SKey

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)
