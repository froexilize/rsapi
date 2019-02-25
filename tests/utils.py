#!/usr/bin/env python
# -*- coding: utf-8 -*-

import binascii
def load_pub_key(key_dir = None):
    path1 = "public.key"

    if key_dir != None:
        path1 = key_dir + path1
    with open(path1,"rb") as public_binary :
        p_key = public_binary.read()
        p_key = binascii.hexlify(p_key)

    return p_key

def load_keys(key_dir = None):
    path1 = "public.key"
    path2 = "private.key"

    if key_dir != None :
        path1 = key_dir + path1
        path2 = key_dir + path2

    with open(path1,"rb") as public_binary :
        p_key = public_binary.read()
        p_key = binascii.hexlify(p_key)
    with open(path2,"rb") as private_binary :
        pr_key = private_binary.read()
        pr_key = binascii.hexlify(pr_key)

    return (p_key,pr_key)