import pyEAEAE

keys = dict()

# d stores map from '0' to 'ff', '1' to 'fg' and so on
d = {}

# d_inv stores map from 'ff' to '0', 'fg' to '1' and so on till mu
d_inv = {}

# populate d
count = 0
for i in range(8):
    for j in range(16):
        d[str(count)] = chr(102 + i) + chr(102 + j)
        count += 1
#print d

# populate d_inv
for (key, value) in d.iteritems():
    d_inv[value] = key

# convert our input to input vector using d_inv
def convert(inp):
    i = 0
    res = []
    l = len(inp) / 2
    while i < l:
        bigram = inp[2*i:2*i+2]
        if bigram in d_inv:
            tmp = int(d_inv[bigram])
        else:
            tmp = (ord(bigram[0]) + ord(bigram[1])) % 128
        res.append(tmp)
        i += 1
    return res

# convert input vector to our output using d
def convert_inv(inp):
    i = 0
    res = ''
    l = len(inp)
    while i < l:
        res += d[str(inp[i])]
        i += 1
    return res

# pad input with 'f' till it becomes a multiple of 16
def round(inp):
    rem = 16 - len(inp) % 16
    if rem != 16:
        inp = inp + "f" * rem
    return inp

def encryptAux(s, teamname):
    # convert input to input vector
    inpVec = convert(s)

    # encrypt
    y = pyEAEAE.encrypt(inpVec, keys[teamname])

    # convert to our format and return
    return convert_inv(y)

# main encryption function to be called from outside
def eaeaeEncryption(s, teamname):
    s = round(s)
    l = len(s)
    res = ''
    i = 0
    while i < l:
        res += encryptAux(s[i:i+16], teamname)
        i += 16
    return res

