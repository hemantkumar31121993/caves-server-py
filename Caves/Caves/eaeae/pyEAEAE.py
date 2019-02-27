#/usr/bin/python

def galoisMult(a,b):
    p = 0
    hiBitSet = 0
    for i in range(7):
        if b & 1 == 1:
            p ^= a
        hiBitSet = a & 0x40
        a <<= 1
        if hiBitSet == 0x40:
            a ^= 0x03
        b >>= 1
    return p % 128

# for caching multiplication
mult = []
for i in range(0, 128):
    mult.append([])
    for j in range(0, 128):
        mult[i].append(galoisMult(i, j))

def exp(a, b):
    x = 1
    for i in range(b):
        x = mult[x][a]
    return x

# for caching exponentiation
power = []
for i in range(0, 128):
    power.append([])
    for j in range(0, 128):
        power[i].append(exp(i, j))


def exponentiation(column, E):
    result = []
    for i in range(8):
        result.append(power[column[i]][E[i]])
        #result.append(exp(column[i], E[i]))
    return result

def mixColumn(column, A):
    result = []
    for i in range(8):
        temp = 0
        for j in range(8):
            temp ^= mult[A[i][j]][column[j]]
            #temp ^= galoisMult(A[i][j], column[j])
        result.append(temp)
    return result

def encrypt(I, key):
    I1 = exponentiation(I, key[1])
    I2 = mixColumn(I1, key[0])
    I3 = exponentiation(I2, key[1])
    I4 = mixColumn(I3, key[0])
    I5 = exponentiation(I4, key[1])
    return I5


