#!/usr/bin/env python
# -*- coding: utf-8 -*-
from . import structs as s
from . import proto
import logging
import socket


class Client(object):
    host = '127.0.0.1'
    port = 38100
    connected = False
    sock_timeout = 1000
    request = None
    response = None

    private_key = None
    public_key = None

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.sock_timeout is not None:
            self.sock.settimeout(self.sock_timeout)

    def connect(self, host=None, port=None):
        if host is not None:
            self.host = host
        if port is not None:
            self.port = port
        server_address = (self.host, self.port)
        try:
            self.sock.connect(server_address)
            self.connected = True
        except Exception as e:
            logging.error(str(e))

    def disconnect(self):
        if self.connected:
            self.sock.close()

    def is_connected(self):
        if self.connected:
            return True
        logging.error("no connection")
        return False

    def send_data(self):
        self.sock.sendall(self.request.buffer.raw)
        req_term = proto.TerminatingBlock()
        req_term.pack()
        self.sock.sendall(req_term.buffer.raw)

    def recv_data(self,cmd):
        self.response = proto.Header()
        if self.response.structure.size != 0:
            self.sock.recv_into(self.response.buffer,
                                self.response.structure.size)
        self.response.unpack()
        if not self.response.check_cmd_num(cmd):
            return False
        return True


    def set_keys(self,pub_key,pr_key):
        self.public_key = pub_key
        self.private_key = pr_key


    #Api methods
    def get_balance(self):
        if not self.is_connected():
            return
        self.request = proto.GetBalance()
        self.send_data()

        if self.recv_data('SendBalance') != True:
            return

        balance = proto.Balance()
        self.sock.recv_into(balance.buffer, balance.structure.size)
        balance.unpack()

        resp_term = proto.TerminatingBlock()
        self.sock.recv_into(resp_term.buffer, resp_term.structure.size)
        resp_term.unpack()

        amount = s.Amount()
        amount.set_amount(balance.integral, balance.fraction)

        return amount

    def get_counters(self):
        if not self.connected:
            logging.error("no connection")
            return

        self.request = proto.GetCounters()
        self.send_data()

        if self.recv_data('SendCounters') != True:
            return

        r_counters = proto.Counters()
        self.sock.recv_into(r_counters.buffer, r_counters.structure.size)
        r_counters.unpack()

        resp_term = proto.TerminatingBlock()
        self.sock.recv_into(resp_term.buffer, resp_term.structure.size)
        resp_term.unpack()

        counters = s.Counters()
        counters.set_vals(r_counters.blocks, r_counters.transactions)
        return counters

    def get_last_hash(self):
        if not self.is_connected():
            return

        self.request = proto.GetLastHash()
        self.send_data()

        if self.recv_data('SendLastHash') != True:
            return

        r_block_hash = proto.BlockHash()
        self.sock.recv_into(r_block_hash.buffer, r_block_hash.structure.size)
        r_block_hash.unpack()

        resp_term = proto.TerminatingBlock()
        self.sock.recv_into(resp_term.buffer, resp_term.structure.size)
        resp_term.unpack()

        block = s.Block()
        block.set_hash(r_block_hash.get_hash())
        return block

    def get_block_size(self, block_hash):
        if not self.is_connected():
            return
        self.request = proto.GetBlockSize(block_hash)
        self.send_data()

        if self.recv_data('SendBlockSize') != True:
            return

        r_block_hash = proto.BlockHash()
        self.sock.recv_into(r_block_hash.buffer, r_block_hash.structure.size)
        r_block_hash.unpack()

        block_size = proto.BlockSize()
        self.sock.recv_into(block_size.buffer, block_size.structure.size)
        block_size.unpack()

        resp_term = proto.TerminatingBlock()
        self.sock.recv_into(resp_term.buffer, resp_term.structure.size)
        resp_term.unpack()

        block_size = block_size.values[0]
        return block_size

    def get_transactions(self, block_hash, offset, limit):
        if not self.is_connected():
            return
        self.request = proto.GetTransactions(block_hash, offset, limit)
        self.send_data()

        self.response = proto.Header()
        self.sock.recv_into(self.response.buffer, self.response.structure.size)
        self.response.unpack()

        txs = []
        if not self.response.check_cmd_num('SendTransactions'):
            return txs
        if not self.response.check():
            return txs

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
            self.sock.recv_into(tx.buffer, tx.structure.size)
            tx.unpack()
            #pprint(tx.values)
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

    #TODO sign Transaction
    def get_fee(self,amount):
        if not self.is_connected():
            logging.error("no connection")
            return

        self.request = proto.GetFee(amount)
        self.send_data()
        if not self.recv_data('SendFee') and \
                not self.response.check():
            return

        fee = proto.Balance()
        self.sock.recv_into(fee.buffer,fee.structure.size)
        fee.unpack()

        resp_term = proto.TerminatingBlock()
        self.sock.recv_into(resp_term.buffer, resp_term.structure.size)
        resp_term.unpack()

        _amount = s.Amount()
        _amount.set_amount(fee.integral, fee.fraction)
        return _amount


    def send_transaction(self,target,
                         intg,frac):
        if not self.is_connected():
            logging.error("no connection")
        return False

        t = s.Transaction()
        t.hash_hex = (b'c1c02d12cdadbc73da73cbd9985b2a41ffdb8dba9de470eaab453cc3595'
                      b'eab31f84bbe0766aea98b7ab5487eb5f962fc9c3ed6b6119600428d55ba'
                      b'd383be5020')
        t.sender_public = self.public_key
        t.receiver_public = target
        t.amount.integral = intg
        t.amount.fraction = frac
        t.currency = b'RAS'

        # import racrypt
        # from os import path
        #
        # lib = racrypt.RaCryptLib()
        # pprint(path.dirname(racrypt.__file__))
        # lib.load(path.dirname(racrypt.__file__))
        # lib.sign(
        #   data,self.public_key,
        #   self.private_key
        # )

        self.request = proto.SendTransaction(t)
        self.send_data()
        if self.recv_data('SendBalance') != True:
            return False

        resp_term = proto.TerminatingBlock()
        self.sock.recv_into(resp_term.buffer, resp_term.structure.size)
        resp_term.unpack()

        return True

