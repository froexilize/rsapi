#!/usr/bin/env python
# -*- coding: utf-8 -*-


import rsapi.client
import unittest
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


class TestClient(unittest.TestCase):
    key_dir = '../keys/'

    def __init__(self, *args, **kwargs):
        super(TestClient, self).__init__(*args, **kwargs)
        self.host = '95.84.138.232'
        self.port = 38101

        self.test_client = rsapi.apiClient()
        #self.key1, self.key2 = load_keys(self.key_dir)
        #self.test_client.set_keys(self.key1,self.key2)


    def setUp(self):
        self.test_client._handler.connect(host=self.host, port=self.port)


    def tearDown(self):
        self.test_client._handler.disconnect()


    @unittest.skip("GetBalance")
    def test_get_balance(self):
        amount = self.test_client.get_balance()

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
        self.assertIsInstance(counters, rsapi.Counters)
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
        self.assertIsInstance(t,rsapi.Transaction)

    @unittest.skip("transactionsbykey")
    def test_get_transactionsbykey(self):
        offset = 0
        limit = 7931

        test_key = load_pub_key(self.key_dir)

        self.test_client.send_info(test_key)
        txs = self.test_client.get_transactionsbykey(offset, limit)

        self.assertIsNotNone(self.test_client.response)
        self.assertTrue(self.test_client.response.check())

        print("Get transactions:")
        # for tx in txs:
        #     print(tx.hash_hex)
        #     print(vars(tx))
        #     print(vars(tx.amount))

        print(len(txs))

    #@unittest.skip("get_fee")
    def test_get_fee(self):
        #test_key = load_pub_key(self.key_dir)
        test_key = (b'c1c02d12cdadbc73da73cbd9985b2a41ffdb8dba9de470eaab453cc3595'
                   b'eaead')
        test_key = binascii.unhexlify(test_key)
        temp = rsapi.Amount()
        temp.integral = 1000
        temp.fraction = 0

        self.test_client.send_info(test_key)
        fee = self.test_client.get_fee(temp)


        self.assertIsNotNone(self.test_client._handler.response)
        self.assertTrue(self.test_client._handler.response.check())
        self.assertEqual(fee.integral,100)
        self.assertEqual(fee.fraction,0)

    @unittest.skip("send_info")
    def test_send_info(self):
        resp_key = self.test_client.send_info(self.key1)
        print(binascii.hexlify(resp_key))
        self.assertTrue(True)


    @unittest.skip("SendTransation")
    def test_send_transaction(self):
        self.test_client.send_info(self.key1)

        target = self.key1
        integral = 100
        fraction = 0


        ok = self.test_client.send_transaction(target,
                                               integral,
                                               fraction)

        self.assertIsNotNone(self.test_client.response)
        self.assertTrue(self.test_client.response.check())

if __name__ == '__main__':
    unittest.main()
