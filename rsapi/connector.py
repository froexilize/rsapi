#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import socket
from . import proto
"""
    Create proto structure
"""
def _createGetProto(type, *args):
    _proto = None
    if len(args) != 1:
        return _proto

    if type == proto.CMD_NUMS['GetBalance']:
        _proto = proto.GetBalance()
    elif type == proto.CMD_NUMS['GetLastHash']:
        _proto = proto.GetLastHash()
    elif type == proto.CMD_NUMS['GetCounters']:
        _proto = proto.GetCounters()
    elif type == proto.CMD_NUMS['GetBlockSize']:
        hash, wtf = args[0]
        _proto = proto.GetBlockSize(hash)
    elif type == proto.CMD_NUMS['GetBlocks']:
        offset, limit = args[0]
        _proto = proto.GetBlocks(offset, limit)
    elif type == proto.CMD_NUMS['GetTransaction']:
        block_hash, t_hash = args[0]
        _proto = proto.GetTransaction(block_hash,t_hash)
    elif type == proto.CMD_NUMS['GetTransactions']:
        b_hash, wtf, offset, limit = args[0]
        _proto = proto.GetTransactions(b_hash, offset, limit)
    elif type == proto.CMD_NUMS['GetTransactionsByKey']:
        offset, limit = args[0]
        _proto = proto.GetTransactionsByKey(offset, limit)
    elif type == proto.CMD_NUMS['GetFee']:
        amount, wft = args[0]
        _proto = proto.GetFee(amount)
    elif type == proto.CMD_NUMS['CommitTransaction']:
        t, wtf = args[0]
        _proto = proto.SendTransaction(t)
    elif type == proto.CMD_NUMS['GetInfo']:
        key, wft = args[0]
        _proto = proto.GetInfo(key)
    return _proto

"""
    create answer 
"""
def _createStruct(type):
    _s = None
    _s = proto.BlockHash()
    if type == proto.CMD_NUMS['GetFee']:
        _s = proto.Balance()
    if type == proto.CMD_NUMS['GetBalance']:
        _s = proto.Balance()
    elif type == proto.CMD_NUMS['GetInfo']:
        _s = proto.PublicKey()
    elif type == proto.CMD_NUMS['GetCounters']:
        _s = proto.Counters()
    elif type == proto.CMD_NUMS['GetTransactionsByKey']:
        _s = proto.Balance()
    return _s



class Connector(object):
    host = '127.0.0.1'
    port = 38100
    sock_timeout = 100
    connected = False
    request = None
    response = None
    need_notify = False

    def __init__(self):
        self.create_socket()

    def __del__(self):
        self.disconnect()

    def create_socket(self):
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

        #Specify type of error
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


    def _createStruct(self, _type):
        _s = _createStruct(_type)

        if _s == None:
            print('Error to create Struct')
            return
        self.sock.recv_into(_s.buffer, _s.structure.size)
        _s.unpack()

        return _s

    #TODO notify client about resend
    def send_data(self):
        try:
            self.sock.sendall(self.request.buffer.raw)
            req_term = proto.TerminatingBlock()
            req_term.pack()
            self.sock.sendall(req_term.buffer.raw)
        except socket.timeout:
            self.create_socket()
            self.connect()
            self.send_data()

    #TODO try expect block
    def recv_cmd(self, cmd):
        self.response = proto.Header()
        if self.response.structure.size != 0:
            self.sock.recv_into(self.response.buffer,
                                self.response.structure.size)
        self.response.unpack()
        if not self.response.cmd_num == cmd:
            return False
        return True

    def recv_into(self, type):
        result = None
        if type == 'Transaction':
            result = proto.Transaction()
        elif type == 'BlockHash':
            result = proto.BlockHash()
        elif type == 'BlockSize':
            result = proto.BlockSize()

        self.sock.recv_into(result.buffer,
                            result.structure.size)
        result.unpack()

        return result

    def recv_term_block(self):
        resp_block = proto.TerminatingBlock()
        self.sock.recv_into(resp_block.buffer, resp_block.structure.size)
        resp_block.unpack()


    def method(self, *argc, _type, term_block):
        self.request = _createGetProto(_type, argc)
        if self.request == None:
            print('Error to create request')
            return None

        self.send_data()
        cmd = _type + 1
        if _type == proto.CMD_NUMS['CommitTransaction']:
            cmd += 1

        ok = self.recv_cmd(cmd)
        if not ok:
            print('Error to check cmd')
            return None

        result = self._createStruct(_type)
        if term_block is True:
            self.recv_term_block()

        return result

