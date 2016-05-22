#!/usr/bin/python

import constants
import binascii
from bitarray import bitarray

# This algorithm currently doesn't applying initial
# permutation and its inverse to blocks


def byte_to_binary(n):
        return ''.join(str((n & (1 << i)) and 1) for i in reversed(range(8)))

def hex_to_binary(h):
        return ''.join(byte_to_binary(ord(b)) for b in binascii.unhexlify(h))

def shuffle(input, perm, mode=None):
    if mode is None:
        output = ""
        for c in perm:
            output += input[c - 1]
        return output
    else:
        output = bitarray()
        for c in perm:
            output.append(input[c - 1])
        return output

def rotate(l,n):
        return l[n:] + l[:n]

def generateKeys(keys_components):
    left = keys_components[0][0]
    right = keys_components[0][1]
    for item in constants.shifts:
        left = rotate(left, item)
        right = rotate(right, item)
        keys_components.append((left, right))
    keys = [];
    for item in keys_components[1:17]:
        keys.append(bitarray(shuffle(item[0] + item[1], constants.pc2)))
    return keys

def round(input, multiple):
    output = input
    rem = multiple - (len(input) % multiple)
    if rem != multiple:
        output += "\x00" * rem
    return output

def expand(input):
    return shuffle(input, constants.expand, "Binary")

def mapSBox(sBox, input):
    row = bitarray()
    row.append(input[0])
    row.append(input[5])
    column = input[1:5]
    row_int = int(row.to01(), 2)
    column_int = int(column.to01(),2)
    out = format(sBox[row_int][column_int], 'b').zfill(4)
    return bitarray(out)

def f(input, key):
    expanded_right = expand(input)
    xored_right = expanded_right ^ key
    sboxed_right = bitarray()
    for j in range(0, 8):
        sBox = constants.sBoxes[j]
        sboxed_right.extend(mapSBox(constants.sBoxes[j], xored_right[j*6:(j+1)*6]))
    permuted_right = shuffle(sboxed_right, constants.perm, "Binary")
    return permuted_right

def encryptDES(input, steps, keys):
    blocks = len(input)/64
    output = bitarray()
    for i in range(0, blocks):
        output.extend(encryptDESAux(input[i*64:(i+1)*64], steps, keys))
    return output

def encryptDESAux(input, steps, keys):
    left = input[0:32]
    right = input[32:64]
    for i in range(0, steps):
        permuted_right = f(right, keys[i])
        leftnew = right
        right = left ^ permuted_right
        left = leftnew
    output = bitarray()
    output.extend(left)
    output.extend(right)
    return output

def decryptDES(input, steps, keys):
    blocks = len(input)/64
    output = bitarray()
    for i in range(0, blocks):
        output.extend(decryptDESAux(input[i*64:(i+1)*64], steps, keys))
    return output

def decryptDESAux(input, steps, keys):
    left = input[0:32]
    right = input[32:64]
    for i in range(0, steps):
        permuted_right = f(left, keys[steps - 1 - i])
        rightnew = left
        left = right ^ permuted_right
        right = rightnew
    output = bitarray()
    output.extend(left)
    output.extend(right)
    return output

