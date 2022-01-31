from numpy.core.defchararray import lower

from utils.coder import encodeDevAddr, decode_data_payload_to_mac_commands
from utils.payload_util import encrypt_frm_payload
import base64

appKey = "a772a9b9c627b3a41370b8a8646e6e80"
string = "B97D23A0CDB77A195F29C38EA67BF58AA2D62F"
string_dec = "070880DE8C50070950E68C50070A20EE8C5006"
netSKey = "5A3D5BE4BF000B4A760C6B59A379AEA9".lower()
string_dec_byte_ok = bytes.fromhex(string_dec)
dev_addr = "01079ba9"
dev_addr_byte = encodeDevAddr(int(dev_addr, 16).to_bytes(4, 'little'))
string_dec = encrypt_frm_payload(netSKey, False, dev_addr_byte, 0, bytearray(bytes.fromhex(string)))
print(string_dec==string_dec_byte_ok)
print(string_dec_byte_ok)
#string_dec = "070880DE8C50070950E68C50070A20EE8C5006"
#mac_comms = decode_data_payload_to_mac_commands(False, [bytes.fromhex(string_dec)])
#print(mac_comms)