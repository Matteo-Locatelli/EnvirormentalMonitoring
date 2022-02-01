from payloads.mac_layer.phy_payload import Frame
from utils.coder import encodeDevAddr, decode_frm_payload_to_mac_commands, encode_mac_commands_to_frm_payload
from utils.payload_util import encrypt_frm_payload, getJsonFromObject
import base64

appKey = "a772a9b9c627b3a41370b8a8646e6e80"
string = "wdb/xABHjN5AXLeuWZs="
string_dec = "eyJodW1pZGl0eSI6NX0="
frames = [Frame(string)]
netSKey = "EA9DCDF217627C458A1A4B408200B608"
appSKey = "87CDAF7049383DD608FBBEBA40B65507"

string2 = "ei5cHmCQYh72t2aRhxG8qMta/w=="
netSkey2 = "241CC39F85BD9D7C3D0EA2F21F041995"
dev_addr = "002ebab7"
dev_addr2 = "01e9d63c"
dev_addr_byte = encodeDevAddr(int(dev_addr, 16).to_bytes(4, 'little'))
dev_addr_byte2 = encodeDevAddr(int(dev_addr2, 16).to_bytes(4, 'little'))
d = encrypt_frm_payload(appSKey, netSKey, 1, True, dev_addr_byte, 317, bytearray(base64.b64decode(string_dec)))
mac_dec_list = decode_frm_payload_to_mac_commands(appSKey, netSkey2, 0, False, dev_addr2, 1, [Frame(string2)])
for mac_dec in mac_dec_list:
    print(getJsonFromObject(mac_dec))

mac_dec_list_encoded = encode_mac_commands_to_frm_payload(appSKey, netSkey2, 0, False, dev_addr2, 1, mac_dec_list)
print("Expected", string2)
print("Obtained", mac_dec_list_encoded)
mac_dec_list = decode_frm_payload_to_mac_commands(appSKey, netSkey2, 0, False, dev_addr2, 1, [Frame(mac_dec_list_encoded)])
for mac_dec in mac_dec_list:
    print(getJsonFromObject(mac_dec))

