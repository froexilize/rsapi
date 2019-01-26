#!/usr/bin/env python
# -*- coding: utf-8 -*-


from api.client import *
import unittest
import binascii
import sys


def load_keys(key_dir = None):
    path1 = "public.key"
    path2 = "private.key"

    if key_dir != None :
        path1 = key_dir + path1
        path2 = key_dir + path2

    with open(path1,"rb") as public_binary :
        p_key = public_binary.read()
        key1 = binascii.hexlify(p_key)

    with open(path2,"rb") as private_binary :
        pr_key = private_binary.read()
        key2 = binascii.hexlify(pr_key)

    return (key1,key2)


class TestClient(unittest.TestCase):
    key_dir = 'keys/'
    def __init__(self, *args, **kwargs):
        super(TestClient, self).__init__(*args, **kwargs)
        self.host = '10.0.0.61'
        self.port = 38100

        key1,key2 = load_keys(self.key_dir)

        self.test_client = Client()
        self.test_client.set_keys(key1,key2)


    def setUp(self):
        self.test_client.connect(host=self.host, port=self.port)

    def tearDown(self):
        self.test_client.disconnect()

    @unittest.skip("GetBalance")
    def test_get_balance(self):
        amount = self.test_client.get_balance()

        print()

        self.assertIsNotNone(self.test_client.response)
        if self.test_client.response is not None:
            self.assertTrue(self.test_client.response.check())
            self.assertEqual(amount.integral, 32768)
            self.assertEqual(amount.fraction, 10)

    @unittest.skip("GetCounters")
    def test_get_counters(self):
        counters = self.test_client.get_counters()

        self.assertIsNotNone(self.test_client.response)
        self.assertTrue(self.test_client.response.check())
        self.assertIsInstance(counters, Counters)
        self.assertEqual(counters.blocks, 250)
        self.assertEqual(counters.transactions, 123456)

    @unittest.skip("GetLastHash")
    def test_get_last_hash(self):
        last_hash = self.test_client.get_last_hash()

        self.assertIsNotNone(self.test_client.response)
        if self.test_client.response is not None:
            self.assertTrue(self.test_client.response.check())
            self.assertEqual(len(last_hash.hash), 64)
            self.assertEqual(len(last_hash.hash_hex), 128)

    @unittest.skip("GetBlockSize")
    def test_get_block_size(self):
        block_hash = (b'c1c02d12cdadbc73da73cbd9985b2a41ffdb8dba9de470eaab453cc'
                      b'3595eab31f84bbe0766aea98b7ab5487eb5f962fc9c3ed6b6119600'
                      b'428d55bad383be5020')
        block_size = self.test_client.get_block_size(block_hash)

        self.assertIsNotNone(self.test_client.response)
        if self.test_client.response is not None:
            self.assertTrue(self.test_client.response.check())
            self.assertEqual(block_size, 123456)

    @unittest.skip("GetTransactions")
    def test_get_transactions(self):
        block_hash = (b'c1c02d12cdadbc73da73cbd9985b2a41ffdb8dba9de470eaab453cc'
                      b'3595eab31f84bbe0766aea98b7ab5487eb5f962fc9c3ed6b6119600'
                      b'428d55bad383be5020')
        offset = 2
        limit = 5
        txs = self.test_client.get_transactions(block_hash, offset, limit)

        self.assertIsNotNone(self.test_client.response)
        self.assertTrue(self.test_client.response.check())
        self.assertEqual(len(txs), 5)

    @unittest.skip("GetBlocks")
    def test_get_blocks(self):
        offset = 0
        limit = 5
        blocks = self.test_client.get_blocks(offset, limit)
        self.assertIsNotNone(self.test_client.response)
        self.assertTrue(self.test_client.response.check())
        self.assertGreater(len(blocks), 0)

    @unittest.skip("GetTransaction")
    def test_get_transaction(self):
        b_hash = (b'c1c02d12cdadbc73da73cbd9985b2a41ffdb8dba9de470eaab453cc3595'
                  b'eab31f84bbe0766aea98b7ab5487eb5f962fc9c3ed6b6119600428d55ba'
                  b'd383be5020')
        t_hash = (b'c1c02d12cdadbc73da73cbd9985b2a41ffdb8dba9de470eaab453cc3595'
                  b'eab31f84bbe0766aea98b7ab5487eb5f962fc9c3ed6b6119600428d55ba'
                  b'd383be5021')
        t = self.test_client.get_transaction(b_hash, t_hash)
        self.assertIsNotNone(self.test_client.response)
        self.assertTrue(self.test_client.response.check())
        self.assertIsInstance(t,Transaction)

    def test_get_transactionsbukey(self):
        offset = 3
        limit = 35
        const_pubkey = (b'50f86b12dbdb50ae9197980787198e278dc9ec94ec8491e3b79df031'
                        b'57ad0bd1')
        any_pubkey = binascii.unhexlify(const_pubkey)
        txs = self.test_client.get_transactionsbykey(any_pubkey, offset, limit)

        self.assertIsNotNone(self.test_client.response)
        self.assertTrue(self.test_client.response.check())
        # self.assertEqual(len(txs), 5)
        pprint("Get transactions:")
        for tx in txs:
            pprint(tx.hash_hex)
            pprint(vars(tx))
            pprint(vars(tx.amount))

    # @unittest.skip("SendTransation")
    def test_send_transaction(self):

        target = b''
        integral = 100
        fraction = 0

        ok = self.test_client.send_transaction(target,
                                               integral,
                                               fraction)
        self.assertTrue(ok)

if __name__ == '__main__':
    unittest.main()
