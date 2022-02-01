from payloads.mac_layer.phy_payload import Frame
from utils.coder import encodeDevAddr, decode_frm_payload_to_mac_commands
from utils.payload_util import encrypt_frm_payload
import base64

appKey = "a772a9b9c627b3a41370b8a8646e6e80"
string = "wdb/xABHjN5AXLeuWZs="
string_dec = "eyJodW1pZGl0eSI6NX0="
frames = [Frame(string)]
netSKey = "EA9DCDF217627C458A1A4B408200B608"
appSKey = "87CDAF7049383DD608FBBEBA40B65507"
dev_addr = "002ebab7"
dev_addr_byte = encodeDevAddr(int(dev_addr, 16).to_bytes(4, 'little'))
d = encrypt_frm_payload(appSKey, netSKey, 1, True, dev_addr_byte, 317, bytearray(base64.b64decode(string_dec)))
print(base64.b64encode(d))

