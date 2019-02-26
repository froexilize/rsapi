#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import socket
from rsapi import proto, proto_manager




class SocketManager(object):
    host = '127.0.0.1'
    port = 38100
    sock_timeout = 100
    manager = None
    connected = False
    proto = None
    response = None
    need_notify = False

    def __init__(self):
        self.manager = proto_manager.ProtoMananger()
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


    #TODO notify client about resend
    def send_data(self):
        try:
            self.sock.sendall(self.proto.buffer.raw)
            req_term = proto.TerminatingBlock()
            req_term.pack()
            self.sock.sendall(req_term.buffer.raw)
        except socket.timeout:
            self.create_socket()
            self.connect()
            self.send_data()

    #TODO try expect block
    def recv_cmd(self, cmd):
        try:
            self.response = proto.Header()
            if self.response.buf_size() is not 0:
                self.sock.recv_into(self.response.buffer,
                                    self.response.buf_size())
            self.response.unpack()
            if cmd is not proto.CMD_NUMS['CommitTransaction']:
                if not self.response.cmd_num == cmd:
                    return False

        except socket.timeout:
            self.create_socket()
            self.connect()
            self.recv_cmd(cmd)

        return True

    def recv_into(self, _type):

        result = self.manager.recv_proto(_type)
        try:
            self.sock.recv_into(result.buffer,
                                result.buf_size())
            result.unpack()
        except socket.timeout:
            self.create_socket()
            self.connect()
            self.recv_into(_type)

        return result

    def recv_term_block(self):
        try:
            resp_block = proto.TerminatingBlock()
            self.sock.recv_into(resp_block.buffer,
                                resp_block.buf_size())
            resp_block.unpack()
        except socket.timeout:
            self.create_socket()
            self.connect()
            self.recv_term_block()


    def method(self, *argc, _type, term_block):

        self.proto = proto_manager.create_proto(_type, argc)
        if self.proto is None:
            return None

        self.send_data()

        cmd = self.manager.form_cmd(_type)
        ok = self.recv_cmd(cmd)

        if not ok:
            return None

        result = self._recv_struct(_type)
        if term_block is True:
            self.recv_term_block()

        return result

    def _recv_struct(self, _type):
        _s = proto_manager.create_struct(_type)

        if _s is None:
            return

        self.sock.recv_into(_s.buffer,
                            _s.buf_size())
        _s.unpack()

        return _s
