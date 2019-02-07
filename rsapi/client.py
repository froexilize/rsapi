#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import proto as p
from . import connector as h
from . import signer
from . import structs as s


class apiClient(object):
    _handler = None
    private_key = None
    public_key = None

    def __init__(self):
       self._handler = h.Connector()

    #wtf method
    def set_keys(self,pub_key,pr_key):
        self.public_key = pub_key
        self.private_key = pr_key

    def get_counters(self):
        if not self._handler.is_connected():
            return

        r_counters = self._handler.method(type=p.CMD_NUMS['GetCounters'])
        if r_counters == None:
            return

        counters = s.Counters()
        counters.set_vals(r_counters.blocks, r_counters.transactions)
        return counters

    def get_last_hash(self):
        if not self._handler.is_connected():
            return

        r_block_hash = self._handler.method(type=h.PROTO_TYPE['LastHash'])

        block = s.Block()
        block.set_hash(r_block_hash.get_hash())
        return block


    def get_block_size(self, block_hash):
        if not self._handler.is_connected():
            return

        block_size = self._handler.method(h.PROTO_TYPE['BlockSize'])

        block_size = block_size.values[0]
        return block_size


    def get_transactions(self, block_hash, offset, limit):
        if not self._handler.is_connected():
            return

        txs = self._handler.method(h.PROTO_TYPE['Transactions'])

        tx_size = proto.calcsize('=%s' % proto.F_TRANSACTION)
        block_size = proto.calcsize('=%s' % proto.F_HASH)
        txs_size = self.response.size - block_size

        r_block_hash = proto.BlockHash()
        self.sock.recv_into(r_block_hash.buffer, r_block_hash.structure.size)
        r_block_hash.unpack()

        if txs_size % tx_size > 0:
            return txs
        txs_count = int(txs_size / tx_size)
        for i in range(0, txs_count):
            tx = proto.Transaction()
            self._connector.recv()
            self.sock.recv_into(tx.buffer, tx.structure.size)
            tx.unpack()
            t = s.Transaction()
            t.parse(tx.values)
            txs.append(t)
        return txs

    def get_blocks(self, offset, limit):
        if not self._handler.is_connected():
            return
        self.request = p.GetBlocks(offset, limit)
        self.send_data()

        if self.recv_data('SendBlocks') != True:
            return

        blocks = []
        if self.response.size == 0:
            return blocks
        block_size = p.calcsize(p.F_HASH)
        if self.response.size % block_size == 0:
            return blocks
        blocks_count = int(self.response.size / block_size)
        for b in range(0, blocks_count):
            block_hash = p.BlockHash()
            self.sock.recv_into(block_hash.buffer, block_hash.structure.size)
            block_hash.unpack()
            block = s.Block()
            block.set_hash(block_hash.get_hash())
            blocks.append(block)
        return blocks

    #TODO issue on Github
    def get_transaction(self, b_hash, t_hash):
        if not self._handler.is_connected():
            return None
        result = self._handler.method(b_hash,t_hash,
                                      type=p.CMD_NUMS['GetTransaction'])

        #TODO parse here

        t = s.Transaction()
        return t


    def send_info(self, key):
        if not self._handler.is_connected():
            return False

        resp_key = self._handler.method(key, 'wtf', type=p.CMD_NUMS['GetInfo'])
        if resp_key == None:
            return None

        return resp_key

    def get_balance(self):
        if not self._handler.is_connected():
            return

        balance = self._handler.method(type=p.CMD_NUMS['GetBalance'])
        if balance == None:
            return None

        amount = s.Amount()
        amount.set_amount(balance.integral, balance.fraction)

        return amount

    def get_transactionsbykey(self, offset, limit):
        if not self._handler.is_connected():
            return

        answer = self._handler.method(offset,limit,
                                   type=p.CMD_NUMS['GetTransactionsByKey'])

        if answer == None:
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

    def get_fee(self,amount):
        if not self._handler.is_connected():
            return False

        fee = self._handler.method(amount,'wft',
                                   type=p.CMD_NUMS['GetFee'])

        _amount = s.Amount()
        _amount.set_amount(fee.integral, fee.fraction)
        return _amount

    def send_transaction(self,target,
                         intg,frac):
        if not self._handler.is_connected():
            return False


        t = signer.transaction(self.private_key,
                                      self.public_key,
                                      target,intg,frac)

        resp_term = self._handler.method(t,'wtf',
                                         type=p.CMD_NUMS['CommitTransaction'])

        return True

