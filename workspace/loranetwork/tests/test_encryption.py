from payloads.mac_layer.phy_payload import Frame
from utils.coder import encodeDevAddr, decode_frm_payload_to_mac_commands

appKey = "a772a9b9c627b3a41370b8a8646e6e80"
string = "oZPZ8Uc4VjdXXtWmyVtLP515ZXTlcnBE+2Lniw=="
frames = [Frame(string)]
netSKey = "5A3D5BE4BF000B4A760C6B59A379AEA9"
dev_addr = "01079ba9"
mac_comms = decode_frm_payload_to_mac_commands(netSKey, False, dev_addr, 0, frames)
print(mac_comms)