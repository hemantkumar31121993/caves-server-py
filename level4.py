import pyDES
import constants

keys = dict()

def inversePerm(perm):
    output = []
    size = len(perm)
    for i in range(0, size):
        output.append(perm.index(i + 1) + 1)
    return output

IPI = inversePerm(constants.ip)
IPINVI = inversePerm(constants.ipinv)

count = 0

# d stores map from '0' to 'ff', '1' to 'fg' and so on
d = {}

# d_inv stores map from 'ff' to '0', 'fg' to '1' and so on
d_inv = {}

# populate d
for i in range(16):
    for j in range(16):
        d[str(count)] = chr(102 + i) + chr(102 + j)
        count += 1

# populate d_inv
for (key, value) in d.iteritems():
    d_inv[value] = key

# convert our input to actual binary input using d_inv
def convert(inp):
    i = 0
    res = ''
    l = len(inp) / 2
    while i < l:
        bigram = inp[2*i:2*i+2]]  
        if bigram in d_inv:     
            tmp = format(int(d_inv[inp[2*i:2*i+2]]), 'b').zfill(8)
        else:
            tmp = "01010101"
        res += tmp
        i += 1
    return res


# convert actual binary output to out output using d
def convert_inv(inp):
    i = 0
    res = ''
    l = len(inp) / 8
    while i < l:
        res += d[str(int(inp[8*i:8*i+8], 2))]
        i += 1
    return res

def round(inp):
    rem = 16 - len(inp) % 16
    if rem != 16:
        inp = inp + "ff" * x
    return inp
    

def encrypt_aux(s):
    # convert input to bitarray
    b = bitarray(convert(s))

    # apply initial permutation
    y = shuffle(b, constants.ip, 'binary')

    # encrypt 
    message_bitarray = encryptDES(y, 6, keys[teamname])

    # applu initial permutation inverse
    mbs = shuffle(message_bitarray, constants.ipinv, 'binary')

    # convert bitarray to string
    message_binary = mbs.to01()

    # convert to our format and return
    return convert_inv(message_binary)

def desEncryption(s, teamname):
    l = len(round(s))
    res = ''
    i = 0
    while i < l:
        res += encrypt_aux(s[i:i+16], teamname)
        i += 16
    return res


def decrypt_aux(s):
    b = bitarray(convert(s))

    y = shuffle(b, IPINVI, 'binary')

    message_bitarray = decryptDES(y, 6, keys)

    mbs = shuffle(message_bitarray, IPI, 'binary')

    message_binary = mbs.to01()
    return convert_inv(message_binary)


def decrypt_main(s):
    l = len(s)
    res = ''
    i = 0
    while i < l:
        res += decrypt_aux(s[i:i+16])
        i += 16
    return res


