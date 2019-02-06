#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import proto
from . import connector as h
from . import signer
from . import structs as s



def createProto(self, type):
    pass

class apiClient(object):
    _connector = None
    private_key = None
    public_key = None

    def __init__(self):
       self._connector = h.connector()

    #wtf method
    def set_keys(self,pub_key,pr_key):
        self.public_key = pub_key
        self.private_key = pr_key

    #Api methods
    def get_balance(self):
        if not self._connector.is_connected():
            return

        balance = self._handler.method(h.PROTO_TYPE['Balance'])
        if balance == None:
            #TODO error
            return None


        amount = s.Amount()
        amount.set_amount(balance.integral, balance.fraction)

        return amount

    def get_counters(self):
        if not self._connector.is_connected():
            return

        r_counters = self._handler.method(h.PROTO_TYPE['Counters'])
        if r_counters == None:
            return

        # self.request = proto.GetCounters()
        # self.send_data()
        #
        # if self.recv_data('SendCounters') != True:
        #     return
        #
        # r_counters = proto.Counters()
        # self.sock.recv_into(r_counters.buffer, r_counters.structure.size)
        # r_counters.unpack()
        #
        # resp_term = proto.TerminatingBlock()
        # self.sock.recv_into(resp_term.buffer, resp_term.structure.size)
        # resp_term.unpack()

        counters = s.Counters()
        counters.set_vals(r_counters.blocks, r_counters.transactions)
        return counters

    def get_last_hash(self):
        if not self._connector.is_connected():
            return

        (r_block_hash, term_block) = self._handler.method(h.PROTO_TYPE['LastHash'])


        # self.request = proto.GetLastHash()
        # self.send_data()
        #
        # if self.recv_data('SendLastHash') != True:
        #     return
        #
        # r_block_hash = proto.BlockHash()
        # self.sock.recv_into(r_block_hash.buffer, r_block_hash.structure.size)
        # r_block_hash.unpack()
        #
        # resp_term = proto.TerminatingBlock()
        # self.sock.recv_into(resp_term.buffer, resp_term.structure.size)
        # resp_term.unpack()

        block = s.Block()
        block.set_hash(r_block_hash.get_hash())
        return block

    #wtf???
    def get_block_size(self, block_hash):
        if not self._connector.is_connected():
            return

        block_size = self._handler.method(h.PROTO_TYPE['BlockSize'])

        # self.request = proto.GetBlockSize(block_hash)
        # self.send_data()
        #
        # if self.recv_data('SendBlockSize') != True:
        #     return
        #
        # r_block_hash = proto.BlockHash()
        # self.sock.recv_into(r_block_hash.buffer, r_block_hash.structure.size)
        # r_block_hash.unpack()
        #
        # block_size = proto.BlockSize()
        # self.sock.recv_into(block_size.buffer, block_size.structure.size)
        # block_size.unpack()
        #
        # resp_term = proto.TerminatingBlock()
        # self.sock.recv_into(resp_term.buffer, resp_term.structure.size)
        # resp_term.unpack()

        block_size = block_size.values[0]
        return block_size

    def get_transactions(self, block_hash, offset, limit):
        if not self.is_connected():
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
        if not self.connected:
            logging.error("no connection")
            return
        self.request = proto.GetBlocks(offset, limit)
        self.send_data()

        if self.recv_data('SendBlocks') != True:
            return

        blocks = []
        if self.response.size == 0:
            return blocks
        block_size = proto.calcsize(proto.F_HASH)
        if self.response.size % block_size == 0:
            return blocks
        blocks_count = int(self.response.size / block_size)
        for b in range(0, blocks_count):
            block_hash = proto.BlockHash()
            self.sock.recv_into(block_hash.buffer, block_hash.structure.size)
            block_hash.unpack()
            block = s.Block()
            block.set_hash(block_hash.get_hash())
            blocks.append(block)
        return blocks

    #TODO issue on Github
    def get_transaction(self, b_hash, t_hash):
        if not self.is_connected():
            return
        self.request = proto.GetTransaction(b_hash, t_hash)
        self.send_data()
        if not self.response.check_cmd_num('SendTransaction'):
            return

        #TODO parse here

        t = s.Transaction()
        return t

    def send_info(self,key):
        if not self.is_connected():
            return

        self.request = proto.GetInfo(key)
        self.send_data()

        if not self.recv_data('SendInfo'):
            print("NOT SEND INFO")
            return

        resp_key = proto.PublicKey()
        self.sock.recv_into(resp_key.buffer, resp_key.structure.size)
        resp_key.unpack()

        resp_term = proto.TerminatingBlock()
        self.sock.recv_into(resp_term.buffer, resp_term.structure.size)
        resp_term.unpack()
        return resp_key

    def get_transactionsbykey(self, offset, limit):
        if not self.is_connected():
            return

        self.request = proto.GetTransactionsByKey(offset, limit)
        self.send_data()

        txs = []

        if not self.recv_data('SendTransactionsByKey'):
            return txs
        if not self.response.check():
            return txs

        tx_size = proto.calcsize('=%s' % proto.F_TRANSACTION)
        block_size = proto.calcsize('=%s' % proto.F_HASH)
        txs_buffer_size = self.response.size - block_size

        r_block_hash = proto.BlockHash()
        self.sock.recv_into(r_block_hash.buffer, r_block_hash.structure.size)
        r_block_hash.unpack()

        if txs_buffer_size % tx_size > 0:
            return txs
        txs_count = int(txs_buffer_size / tx_size)

        for i in range(0, txs_count):
            tx = proto.Transaction()
            self.sock.recv_into(tx.buffer, tx.structure.size)
            tx.unpack()
            t = s.Transaction()
            t.parse(tx.values)
            txs.append(t)

        return txs

    def get_fee(self,amount):
        if not self.is_connected():
            logging.error("no connection")
            return

        (fee, term_block) = self._handler.method(PROTO_TYPE['Fee'])

        # self.request = proto.GetFee(amount)
        # self.send_data()
        # if not self.recv_data('SendFee') and \
        #         not self.response.check():
        #     return
        #
        # fee = proto.Balance()
        # self.sock.recv_into(fee.buffer,fee.structure.size)
        # fee.unpack()
        #
        # resp_term = proto.TerminatingBlock()
        # self.sock.recv_into(resp_term.buffer, resp_term.structure.size)
        # resp_term.unpack()

        _amount = s.Amount()
        _amount.set_amount(fee.integral, fee.fraction)
        return _amount


    def send_transaction(self,target,
                         intg,frac):
        if not self.is_connected():
            logging.error("no connection")
            return False


        t = self._signer.transaction(self.private_key,
                                      self.public_key,
                                      target,intg,frac)


        resp_term = self._connector.method(PROTO_TYPE['SendTransaction'],t)

        # self.request = proto.SendTransaction(t)
        # self.send_data()
        #
        # if self.recv_data('Error') != True:
        #     pass
        # resp_term = proto.TerminatingBlock()
        # self.sock.recv_into(resp_term.buffer, resp_term.structure.size)
        # resp_term.unpack()

        return True

