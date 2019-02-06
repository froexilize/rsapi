#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import socket
from . import proto
from . import structs as s


PROTO_TYPE = {
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


def _createGetProto(self, type, *args):
    _proto = None
    if type == PROTO_TYPE['Balance']:
        _proto = proto.GetBalance()
    elif type == PROTO_TYPE['LastHash']:
        _proto = proto.GetLastHash()
    elif type == PROTO_TYPE['Counters']:
        _proto = proto.GetCounters()
    elif type == PROTO_TYPE['BlockSize']:
        _proto = proto.GetBlockSize()
    elif type == PROTO_TYPE['Blocks']:
        _proto = proto.GetBlocks()
    elif type == PROTO_TYPE['Transaction']:
        _proto = proto.GetTransaction()
    elif type == PROTO_TYPE['Transactions']:
        _proto = proto.GetTransactions()
    elif type == PROTO_TYPE['TransactionByKey']:
        _proto = proto.GetTransactionsByKey()
    elif type == PROTO_TYPE['TerminatingBlock']:
        _proto = proto.TerminatingBlock()
    elif type == PROTO_TYPE['Fee']:
        _proto = proto.GetFee()
    elif type == PROTO_TYPE['SendTransaction']:
        _proto = proto.SendTransaction()
    elif type == PROTO_TYPE['Info']:
        _proto = proto.GetInfo()
    return _proto


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





    def _createProto(self,type,*argc):
        proto = None
        if type == '':
            proto
        elif type == '':
            proto
        self.sock.recv_into(proto.buffer,proto.structure.size)
        proto.unpack()

        resp_block = proto.TerminatingBlock()
        self.sock.recv_into(resp_block.buffer,resp_block.structure.size)
        resp_block.unpack()

        return proto

    def method(self,*argc,type):
        self.request = self._createGetProto(type,argc)
        self.send_data()
        cmd = type+1
        if type == PROTO_TYPE['SendTransaction']:
            cmd += 1
        ok = self.recv_cmd(cmd)
        if not ok:
            return None
        result = self._createProto(type)

        return result