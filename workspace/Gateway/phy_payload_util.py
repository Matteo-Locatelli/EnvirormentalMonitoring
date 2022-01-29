
def compute_mic(data,devAdress,netSessionKey):
    # based on https://lora-alliance.org/sites/default/files/2018-04/lorawantm_specification_-v1.1.pdf#page=27
    cmac = AES_CMAC() #non so da dove prenderlo

    fcntup = [0x00, 0x00, 0x00, 0x00]

    b0 = [0x49, 0x00, 0x00, 0x00, 0x00]
    b0 += [0x00] #dir
    b0 += devAdress[::-1]
    b0 += fcntup
    b0 += [0x00]
    b0 += [len(data)]
    b0 += data

    b1 = [0x49, 0x00, 0x00]
    b1 += [0x02] #txdr
    b1 += [0x00] #txch
    b1 += [0x00] #dir
    b1 += devAdress[::-1]
    b1 += fcntup
    b1 += [0x00]
    b1 += [len(data)]
    b1 += data

    sn_mic = cmac.encode(bytes(netSessionKey), bytes(b1))[:2]
    fn_mic = cmac.encode(bytes("config['fnwksintkey']"), bytes(b0))[:2]
    mic = list(map(int, sn_mic))
    mic += list(map(int, fn_mic))
    return mic