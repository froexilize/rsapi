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
        self.key1, self.key2 = load_keys(self.key_dir)
        self.test_client.set_keys(self.key1, self.key2)


    def setUp(self):
        self.test_client._handler.connect(host=self.host, port=self.port)


    def tearDown(self):
        self.test_client._handler.disconnect()


    @unittest.skip("GetBalance")
    def test_get_balance(self):
        self.test_client.send_info(self.key1)
        amount = self.test_client.get_balance()

        self.assertIsNotNone(self.test_client._handler.response)
        if self.test_client._handler.response is not None:
            self.assertTrue(self.test_client._handler.response.check())
            self.assertEqual(amount.integral, 4200000000)
            self.assertEqual(amount.fraction, 0)

    @unittest.skip("GetCounters")
    def test_get_counters(self):
        counters = self.test_client.get_counters()

        self.assertIsNotNone(self.test_client._handler.response)
        self.assertTrue(self.test_client._handler.response.check())
        self.assertIsInstance(counters, rsapi.Counters)
        self.assertEqual(counters.blocks, 1)
        self.assertEqual(counters.transactions, 1)

    @unittest.skip("GetLastHash")
    def test_get_last_hash(self):
        last_hash = self.test_client.get_last_hash()

        self.assertIsNotNone(self.test_client.response)
        if self.test_client.response is not None:
            self.assertTrue(self.test_client.response.check())
            self.assertEqual(len(last_hash.hash), 64)
            self.assertEqual(len(last_hash.hash_hex), 128)

    #@unittest.skip("GetBlockSize")
    def test_get_block_size(self):
        b_hash = b'6ba4295e07484597caf7722b59c6206fc6735a0d521927b3f556650a073ff12680d24b3aaa51db' \
                 b'f2096eccaeca8e323e9813cfce2f929881f47b9eac136ae85b'

        block_size = self.test_client.get_block_size(b_hash)

        self.assertIsNotNone(self.test_client._handler.response)
        if self.test_client._handler.response is not None:
            self.assertTrue(self.test_client._handler.response.check())
            self.assertEqual(block_size, 1)


    @unittest.skip("GetBlocks")
    def test_get_blocks(self):
        offset = 0
        limit = 5
        blocks = self.test_client.get_blocks(offset,
                                             limit)


        self.assertIsNotNone(self.test_client._handler.response)
        self.assertTrue(self.test_client._handler.response.check())
        self.assertGreater(len(blocks), 0)


    @unittest.skip("GetTransaction")
    def test_get_transaction(self):
        self.test_client.send_info(self.key1)

        b_hash = b'6ba4295e07484597caf7722b59c6206fc6735a0d521927b3f556650a073ff12680d24b3aaa51db' \
                 b'f2096eccaeca8e323e9813cfce2f929881f47b9eac136ae85b'

        t_hash = (b'4C92993FF1A9E2837E8262B721CE9AC46FDE818DC5A53FC7F8F74644EF06EA996C562ACCEF337D57A78AE'
                  b'00C4FD606362BA514335230A8B33F5903212727AE05')

        t = self.test_client.get_transaction(b_hash, t_hash)


        self.assertIsNotNone(self.test_client._handler.response)
        self.assertTrue(self.test_client._handler.response.check())
        self.assertEqual(t.amount.integral, 241)
        self.assertIsInstance(t, rsapi.Transaction)


    #@unittest.skip("GetTransactions")
    def test_get_transactions(self):
        b_hash = b'6ba4295e07484597caf7722b59c6206fc6735a0d521927b3f556650a073ff12680d24b3aaa51db' \
                 b'f2096eccaeca8e323e9813cfce2f929881f47b9eac136ae85b'

        offset = 0
        limit = 1

        txs = self.test_client.get_transactions(b_hash,
                                                offset,
                                               limit)

        print(len(txs))

        self.assertIsNotNone(self.test_client._handler.response)
        self.assertTrue(self.test_client._handler.response.check())

        self.assertEqual(len(txs), 1)



    @unittest.skip("transactionsbykey")
    def test_get_transactionsbykey(self):
        offset = 0
        limit = 1

        test_key = load_pub_key(self.key_dir)

        self.test_client.send_info(test_key)
        txs = self.test_client.get_transactionsbykey(offset, limit)

        self.assertIsNotNone(self.test_client._handler.response)
        self.assertTrue(self.test_client._handler.response.check())

        print("Get transactions:")
        for tx in txs:
            print(tx.hash_hex)
            print(vars(tx))
            print(vars(tx.amount))

        print(len(txs))

    @unittest.skip("get_fee")
    def test_get_fee(self):
        #test_key = load_pub_key(self.key_dir)
        # test_key = (b'c1c02d12cdadbc73da73cbd9985b2a41ffdb8dba9de470eaab453cc3595'
        #            b'eaead')
        # test_key = binascii.unhexlify(test_key)
        temp = rsapi.Amount()
        temp.integral = 1000
        temp.fraction = 0

        #self.test_client.send_info(test_key)
        fee = self.test_client.get_fee(temp)


        self.assertIsNotNone(self.test_client._handler.response)
        self.assertTrue(self.test_client._handler.response.check())
        self.assertEqual(fee.integral,100)
        self.assertEqual(fee.fraction,0)

    @unittest.skip("send_info")
    def test_send_info(self):
        test_key = load_pub_key(self.key_dir)
        resp_key = self.test_client.send_info(test_key)
        if not resp_key == None:
            print(binascii.hexlify(resp_key.values[0]))
        self.assertTrue(True)


    @unittest.skip("SendTransation")
    def test_send_transaction(self):

        test_key = (b'4b335fb3f5fe4669fa2bc7b384d68c377f4e4c1fec878e82bd09158ddb'
                    b'0c77f2')

        self.test_client.send_info(self.key1)

        amount = self.test_client.get_balance()

        target = test_key
        integral = 761
        fraction = 0

        if amount.integral > integral:
            ok = self.test_client.send_transaction(target,
                                               integral,
                                               fraction)

        self.assertIsNotNone(self.test_client._handler.response)
        #self.assertTrue(self.test_client._handler.response.check())


if __name__ == '__main__':
    unittest.main()
