import base64

from utils.coder import decode_phy_payload, decode_join_accept_mac_payload
from utils.payload_util import get_json_from_object, compute_join_request_mic

app_key = "A772A9B9C627B3A41370B8A8646E6E80".lower()
app_k_t = "00112233445566778899aabbccddeeff"
phy_payload_byte = "IFdUEzW1ejR2C6P7werVeoWYIRhyLT3m5EGdGmD1E4A0"
p_t = "IEk+61H7ohFvgQ7bN0KXUUI="
dev_nonce = 60750
dev_n = 5704647

p = decode_phy_payload(phy_payload_byte)
print(get_json_from_object(p))
print(compute_join_request_mic(base64.b64decode(phy_payload_byte), app_key))
join_accept_mac_payload = decode_join_accept_mac_payload(app_key, dev_nonce, p)
print(get_json_from_object(join_accept_mac_payload))
