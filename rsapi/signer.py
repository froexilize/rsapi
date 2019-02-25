#!/usr/bin/env python
# -*- coding: utf-8 -*-
import racrypt
from os import path
import binascii
import random
from . import structs as s


def transaction(pr_key, from_key, to_key, intg, frac):
    salt_sz = 32
    t = s.Transaction()
    t.sender_public = from_key
    t.receiver_public = to_key
    t.amount.integral = intg
    t.amount.fraction = frac
    t.currency = b'RAS'
    t.salt = bytearray(salt_sz)
    for it in range(salt_sz):
        t.salt[it] = random.randint(0, 255)

    lib = racrypt.Crypto()
    lib.load(path.dirname(racrypt.__file__))

    buffer = bytearray()
    buffer += binascii.unhexlify(t.sender_public)
    buffer += binascii.unhexlify(t.receiver_public)
    buffer += t.amount.integral.to_bytes(4, 'little')
    buffer += t.amount.fraction.to_bytes(8, 'little')
    buffer += t.currency
    buffer += bytearray(16 - len(t.currency))
    buffer += t.salt

    result = lib.sign(
        bytes(buffer), len(buffer),
        binascii.unhexlify(from_key),
        binascii.unhexlify(pr_key),
    )

    if result != True:
        return None

    t.hash_hex = lib.signature


    result = lib.verify(bytes(buffer), len(buffer),
                        binascii.unhexlify(from_key),
                        lib.signature)
    print('verify success', result)

    return t