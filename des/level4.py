import pyDES
import constants
from bitarray import bitarray

keys = dict()

def inversePerm(perm):
    output = []
    size = len(perm)
    for i in range(0, size):
        output.append(perm.index(i + 1) + 1)
    return output

# inverse of initial permutation
IPI = inversePerm(constants.ip)

# inverse of initial permutation inverse
IPINVI = inversePerm(constants.ipinv)

# d stores map from '0' to 'ff', '1' to 'fg' and so on
d = {}

# d_inv stores map from 'ff' to '0', 'fg' to '1' and so on
d_inv = {}

# populate d
count = 0
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
        bigram = inp[2*i:2*i+2]
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

# pad input with 'f' till it becomes a multiple of 16
def round(inp):
    rem = 16 - len(inp) % 16
    if rem != 16:
        inp = inp + "f" * rem
    return inp

def encryptAux(s, teamname):
    # convert input to bitarray
    b = bitarray(convert(s))

    # apply initial permutation
    y = pyDES.shuffle(b, constants.ip, 'binary')

    # encrypt
    message_bitarray = pyDES.encryptDES(y, 6, keys[teamname])

    # apply initial permutation inverse
    mbs = pyDES.shuffle(message_bitarray, constants.ipinv, 'binary')

    # convert bitarray to string
    message_binary = mbs.to01()

    # convert to our format and return
    return convert_inv(message_binary)

# main encryption function to be called from outside
def desEncryption(s, teamname):
    s = round(s)
    l = len(s)
    res = ''
    i = 0
    while i < l:
        res += encryptAux(s[i:i+16], teamname)
        i += 16
    return res


def decryptAux(s, teamname):
    b = bitarray(convert(s))

    y = pyDES.shuffle(b, IPINVI, 'binary')

    message_bitarray = pyDES.decryptDES(y, 6, keys[teamname])

    mbs = pyDES.shuffle(message_bitarray, IPI, 'binary')

    message_binary = mbs.to01()
    return convert_inv(message_binary)

# used for decryption
def desDecryption(s, teamname):
    l = len(s)
    res = ''
    i = 0
    while i <= l - 16:
        res += decryptAux(s[i:i+16], teamname)
        i += 16
    return res


