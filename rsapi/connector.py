#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import socket
from . import proto 
from . import structs as s


PROTO_NUMS = {
    'Balance':1,
    'Counters':2,
    'LastHash':3,
    'BlockSize':4,
    'Transactions':5,
    'Blocks':6,
    'Transaction':7,
    'Info':8,
    'Fee':9,
    'TransactionByKey':10,
    'SendTransaction':11,
    'TerminatingBlock':12
}


def _createGetProto(type, *args):
    _proto = None
    if type == proto.CMD_NUMS['GetBalance']:
        _proto = proto.GetBalance()
    elif type == proto.CMD_NUMS['GetLastHash']:
        _proto = proto.GetLastHash()
    elif type == proto.CMD_NUMS['GetCounters']:
        _proto = proto.GetCounters()
    elif type == proto.CMD_NUMS['GetBlockSize']:
        if len(args) != 2:
            return _proto
        _proto = proto.GetBlockSize(args)
    elif type == proto.CMD_NUMS['GetBlocks']:
        if len(args) != 2:
            return _proto
        _proto = proto.GetBlocks(args)
    elif type == proto.CMD_NUMS['GetTransaction']:
        if len(args) != 2:
            return _proto
        _proto = proto.GetTransaction(args)
    elif type == proto.CMD_NUMS['GetTransactions']:
        if len(args) != 3:
            return _proto
        _proto = proto.GetTransactions(args)
    elif type == proto.CMD_NUMS['GetTransactionByKey']:
        if len(args) != 2:
            return _proto
        _proto = proto.GetTransactionsByKey(args)
    elif type == proto.CMD_NUMS['GetTerminatingBlock']:
        _proto = proto.TerminatingBlock()
    elif type == proto.CMD_NUMS['GetFee']:
        if len(args) != 1:
            return _proto
        _proto = proto.GetFee(args)
    elif type == proto.CMD_NUMS['CommitTransaction']:
        if len(args) != 1:
            return _proto
        _proto = proto.SendTransaction(args)
    elif type == proto.CMD_NUMS['GetInfo']:
        if len(args) != 1:
            return _proto
        _proto = proto.GetInfo(args)
    return _proto

def _createStruct(type):
    _s = None
    if type == proto.CMD_NUMS['GetFee']:
        _s = s.Amount()
    elif type == proto.CMD_NUMS['GetInfo']:
        _s = proto.PublicKey()
    return _s

class Connector(object):
    host = '127.0.0.1'
    port = 38100
    connected = False
    sock_timeout = 1000
    request = None
    response = None

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.sock_timeout is not None:
            self.sock.settimeout(self.sock_timeout)

    def __del__(self):
        self.disconnect()

    def connect(self, host=None, port=None):
        if host is not None:
            self.host = host
        if port is not None:
            self.port = port
        server_address = (self.host, self.port)
        try:
            self.sock.connect(server_address)
            # self.send_info(self.public_key)
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

    def recv_cmd(self, cmd):
        self.response = proto.Header()
        if self.response.structure.size != 0:
            self.sock.recv_into(self.response.buffer,
                                self.response.structure.size)
        self.response.unpack()
        if not self.response.check_cmd_num(cmd):
            return False
        return True


    def _sendProto(self,type):
        _s= _createStruct(type)
        if _s == None:
            print('Error to create Proto')
            return
        self.sock.recv_into(proto.buffer,proto.structure.size)
        _s.unpack()

        resp_block = proto.TerminatingBlock()
        self.sock.recv_into(resp_block.buffer,resp_block.structure.size)
        resp_block.unpack()

        return _s

    def method(self,*argc,type):
        self.request = _createGetProto(type,argc)
        if self.request == None:
            print('Error to create request')
            return
        self.send_data()
        cmd = type+1
        if type == proto.CMD_NUMS['CommitTransaction']:
            cmd += 1
        ok = self.recv_cmd(cmd)
        if not ok:
            print('Error to check cmd')
            return None
        result = self._sendProto(type)

        return result