#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import connector as h
from . import proto as p
from . import signer
from . import structs as s


class apiClient(object):
    _handler = None
    private_key = None
    public_key = None

    def __init__(self):
        self._handler = h.Connector()


    def set_keys(self,
                 pub_key,
                 pr_key):
        self.public_key = pub_key
        self.private_key = pr_key

    def get_counters(self):
        if not self._handler.is_connected():
            return

        r_counters = self._handler.method(
                                    _type=p.CMD_NUMS['GetCounters'])
        if r_counters is None:
            return

        counters = s.Counters()
        counters.set_vals(r_counters.blocks,
                          r_counters.transactions)
        return counters

    def get_last_hash(self):
        if not self._handler.is_connected():
            return

        r_block_hash = self._handler.method(
                                _type=p.CMD_NUMS['GetLastHash'])

        block = s.Block()
        block.set_hash(r_block_hash.get_hash())
        return block

    def get_block_size(self, block_hash):
        if not self._handler.is_connected():
            return

        block_size = self._handler.method(block_hash,
                                          'wtf',
                                          _type = p.CMD_NUMS['GetBlockSize'])

        if block_size is None:
            return

        block_size = block_size.values[0]

        return block_size

    def get_transactions(self,
                         block_hash,
                         offset,
                         limit):
        if not self._handler.is_connected():
            return

        txs_list = self._handler.method(block_hash,
                                        'wft',
                                        offset,
                                        limit,
                                        _type=p.CMD_NUMS['GetTransactions'])


        tx_size = p.calcsize('=%s' % p.F_TRANSACTION)
        block_size = p.calcsize('=%s' % p.F_HASH)
        txs_list_size = self._handler.response.size - block_size


        #self._handler.recv_into('BlockHash')

        if txs_list_size % tx_size > 0:
            return txs_list
        txs_count = int(txs_list_size / tx_size)

        print(txs_count)

        for i in range(0, txs_count):
            tx = self._handler.recv_into('Transaction')
            if tx is None:
                return
            t = s.Transaction()
            t.parse(tx.values)
            txs_list.append(t)

        return txs_list

    def get_blocks(self,
                   offset,
                   limit):
        if not self._handler.is_connected():
            return


        self._handler.method(offset,
                             limit,
                             _type=p.CMD_NUMS['GetBlocks'])

        blocks = []
        block_size = p.calcsize(p.F_HASH)
        blocks_count = int(self._handler.response.size / block_size)

        for b in range(0, blocks_count):
            block_hash = self._handler.recv_into('BlockHash')
            block = s.Block()
            block.set_hash(block_hash.get_hash())
            blocks.append(block)
            
        return blocks

    # TODO issue on Github
    def get_transaction(self,
                        b_hash,
                        t_hash):
        if not self._handler.is_connected():
            return None

        # HOW TO WORKS this method
        tx = self._handler.method(b_hash,
                                  t_hash,
                                  _type=p.CMD_NUMS['GetTransaction'])

        t = s.Transaction()
        t.parse(tx.values)

        return t

    def send_info(self,
                  key):
        if not self._handler.is_connected():
            return False

        # TODO to be able parse single Python tuple
        resp_key = self._handler.method(key,
                                        'wtf',
                                        _type=p.CMD_NUMS['GetInfo'])
        if resp_key is None:
            return None

        return resp_key

    def get_balance(self):
        if not self._handler.is_connected():
            return

        balance = self._handler.method(
            _type=p.CMD_NUMS['GetBalance'])
        if balance is None:
            return None

        amount = s.Amount()
        amount.set_amount(balance.integral,
                          balance.fraction)

        return amount

    def get_transactionsbykey(self,
                              offset,
                              limit):
        if not self._handler.is_connected():
            return

        answer = self._handler.method(offset,
                                      limit,
                                      _type=p.CMD_NUMS['GetTransactionsByKey'])

        if answer is None:
            return

        txs = []
        tx_size = p.calcsize('=%s' % p.F_TRANSACTION)
        block_size = p.calcsize('=%s' % p.F_HASH)
        txs_buffer_size = self._handler.response.size - block_size

        r_block_hash = self._handler.recv_into('BlockHash')

        if txs_buffer_size % tx_size > 0:
            return None
        txs_count = int(txs_buffer_size / tx_size)

        for i in range(0, txs_count):

            tx = self._handler.recv_into('Transaction')
            t = s.Transaction()
            t.parse(tx.values)
            txs.append(t)

        return txs

    def get_fee(self,
                amount):
        if not self._handler.is_connected():
            return False

        fee = self._handler.method(amount,
                                   'wft',
                                   _type=p.CMD_NUMS['GetFee'])

        _amount = s.Amount()
        _amount.set_amount(fee.integral, fee.fraction)
        return _amount

    def send_transaction(self,
                         target,
                         intg,
                         frac):
        if not self._handler.is_connected():
            return False

        t = signer.transaction(self.private_key,
                               self.public_key,
                               target,
                               intg,
                               frac)


        answer = self._handler.method(t,
                                      'wtf',
                                      _type=p.CMD_NUMS['CommitTransaction'])

        return True
