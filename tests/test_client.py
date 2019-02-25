#!/usr/bin/env python
# -*- coding: utf-8 -*-


import rsapi.client
import unittest
from tests.utils import *




class TestClient(unittest.TestCase):
    key_dir = 'test_keys/'

    def __init__(self, *args, **kwargs):
        super(TestClient, self).__init__(*args, **kwargs)
        self.host = '10.0.0.61'
        self.port = 38101

        self.test_client = rsapi.apiClient()


    def setUp(self):
        self.test_client._handler.connect(host=self.host,
                                          port=self.port)


    def tearDown(self):
        self.test_client._handler.disconnect()


    @unittest.skip("GetBalance")
    def test_get_balance(self):
        self.test_client.send_info(self.key1)
        amount = self.test_client.get_balance()

        self.assertIsNotNone(self.test_client._handler.response)
        if self.test_client._handler.response is not None:
            self.assertTrue(self.test_client._handler.response.check())
            #self.assertEqual(amount.integral, 4200000000)
            #self.assertEqual(amount.fraction, 0)

    #@unittest.skip("GetCounters")
    def test_get_counters(self):
        counters = self.test_client.get_counters()

        self.assertIsNotNone(self.test_client._handler.response)
        self.assertTrue(self.test_client._handler.response.check())
        self.assertIsInstance(counters, rsapi.Counters)
        self.assertEqual(counters.blocks, 4)
        self.assertEqual(counters.transactions, 1406)

    #@unittest.skip("GetLastHash")
    def test_get_last_hash(self):
        last_hash = self.test_client.get_last_hash()
        print(last_hash.hash_hex)


        self.assertIsNotNone(self.test_client._handler.response)
        if self.test_client._handler.response is not None:
            self.assertTrue(self.test_client._handler.response.check())
            self.assertEqual(len(last_hash.hash), 64)
            self.assertEqual(len(last_hash.hash_hex), 128)

    #@unittest.skip("GetBlockSize")
    def test_get_block_size(self):
        e_pub_key = (b'12cdadbc73da73cbd9985b2a41ffdb8d')
        self.test_client.send_info(e_pub_key)

        #b_hash = b'6ba4295e07484597caf7722b59c6206fc6735a0d521927b3f556650a073ff12680d24b3aaa51db' \
        #         b'f2096eccaeca8e323e9813cfce2f929881f47b9eac136ae85b'

        b_hash = b'1bb6058bb2e6f7fb44c60f25b5f963b75e49adb89a90aa15a8e48c0ece6c229ad520029bba723960b3f0c81' \
            b'c61bae2378a4ce79d0d722d59b0e5aabfd67cbfea'

        block_size = self.test_client.get_block_size(b_hash)
        print(block_size)

        self.assertIsNotNone(self.test_client._handler.response)
        if self.test_client._handler.response is not None:
            self.assertTrue(self.test_client._handler.response.check())
            self.assertEqual(block_size, 694)


    #@unittest.skip("GetBlocks")
    def test_get_blocks(self):
        offset = 0
        limit = 50
        blocks = self.test_client.get_blocks(offset,
                                             limit)


        self.assertIsNotNone(self.test_client._handler.response)
        self.assertTrue(self.test_client._handler.response.check())
        self.assertGreater(len(blocks), 0)
        self.assertEqual(len(blocks), 4)


    #@unittest.skip("GetTransaction")
    def test_get_transaction(self):
        e_pub_key = (b'12cdadbc73da73cbd9985b2a41ffdb8d')
        self.test_client.send_info(e_pub_key)

        # b_hash = b'6ba4295e07484597caf7722b59c6206fc6735a0d521927b3f556650a073ff12680d24b3aaa51db' \
        #          b'f2096eccaeca8e323e9813cfce2f929881f47b9eac136ae85b'

        b_hash = b'1bb6058bb2e6f7fb44c60f25b5f963b75e49adb89a90aa15a8e48c0ece6c229ad520029bba723960b3f0c81' \
                 b'c61bae2378a4ce79d0d722d59b0e5aabfd67cbfea'

        t_hash = (b'966AFAEF1C3A50F5CC3E5BE43DB73199786BF30810C750AE1559F278858C1E633ACA7FFC080EEE48B7E30E'
                  b'4C3D9797C9BC6E9E9963162FD1E185EBE842A39600')

        t = self.test_client.get_transaction(b_hash, t_hash)


        self.assertIsNotNone(self.test_client._handler.response)
        self.assertTrue(self.test_client._handler.response.check())
        self.assertEqual(t.amount.integral, 37)
        self.assertIsInstance(t, rsapi.Transaction)


    #@unittest.skip("GetTransactions")
    def test_get_transactions(self):
        # b_hash = b'6ba4295e07484597caf7722b59c6206fc6735a0d521927b3f556650a073ff12680d24b3aaa51db' \
        #          b'f2096eccaeca8e323e9813cfce2f929881f47b9eac136ae85b'

        b_hash = b'1bb6058bb2e6f7fb44c60f25b5f963b75e49adb89a90aa15a8e48c0ece6c229ad520029bba723960b3f0c81' \
                 b'c61bae2378a4ce79d0d722d59b0e5aabfd67cbfea'
        offset = 0
        limit = 20

        txs = self.test_client.get_transactions(b_hash,
                                                offset,
                                                limit)

        print(len(txs))
        #for tx in txs:
           #print(binascii.hexlify(tx.)


        self.assertIsNotNone(self.test_client._handler.response)
        self.assertTrue(self.test_client._handler.response.check())

        self.assertEqual(len(txs), 20)



    #@unittest.skip("transactionsbykey")
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

    #@unittest.skip("get_fee")
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
        import racrypt
        from os import path

        lib = racrypt.Crypto()
        lib.load(path.dirname(racrypt.__file__))
        lib.create_keys()

        e_pub_key = binascii.hexlify(lib.public_key)
        e_priv_key = binascii.hexlify(lib.private_key)

        self.test_client.set_keys(e_pub_key, e_priv_key)
        test_key = (b'4b335fb3f5fe4669fa2bc7b384d68c377f4e4c1fec878e82bd09158ddb'
                    b'0c77f2')

        self.test_client.send_info(e_pub_key)

        amount = self.test_client.get_balance()

        target = test_key
        integral = 1
        fraction = 0

        #if amount.integral > integral:
        ok = self.test_client.send_transaction(target,
                                               integral,
                                               fraction)

        self.assertIsNotNone(self.test_client._handler.response)
        #self.assertTrue(self.test_client._handler.response.check())


if __name__ == '__main__':
    unittest.main()
