#!/usr/bin/env python
# -*- coding: utf-8 -*-


from rsapi import proto
import unittest
import binascii


class TestProto(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestProto, self).__init__(*args, **kwargs)


    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_getbalance_proto(self):
        integral = 10
        fraction = 0
        _proto = proto.GetBalance(integral,
                                  fraction)
        #TODO test , how packs

    def test_getcounters_proto(self):
        pass