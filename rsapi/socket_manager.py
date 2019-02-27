#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import socket
from rsapi import proto, proto_manager


class SocketManager(object):
    host = '127.0.0.1'
    port = 38100
    sock_timeout = 10
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

    def reconnect(self):
        self.attemp_reconnect()

    def attemp_reconnect(self):
        while self.connected is False:
            try:
                host = (self.host, self.port)
                result = self.sock.connect(host)
                if result is None:
                    self.connected = True
                else:
                    self.connected = False
            except socket.error as err:
                error_code = err[0]
                if error_code is 56:
                    self.connected = True
                elif error_code is 22:
                    self.connected = False
                    print("attempting to reconnect...")
                    # adding recursive call to attempt connect
                    # after socket is broken
                    self.reconnect()
                elif error_code is 61:
                    self.connected = False
                    print("Server not up, waiting for server and reconnecting...")
                elif error_code is 32:
                    self.connected = False
                    print("Server down, attempting to reconnect...")
                else:
                    self.connected = False


    def send_data(self):
        send_status = False
        while send_status is False:
            try:
                self.sock.sendall(self.proto.buffer.raw)
                req_term = proto.TerminatingBlock()
                req_term.pack()
                self.sock.sendall(req_term.buffer.raw)
                send_status = True
            except socket.error as err:
                    print(err.errno)
                    self.connected = False
                    print("Attempting to connect...")
                    self.reconnect()
                    send_status = False

    def recv_into(self, _type):
        result = self.manager.recv_proto(_type)
        recv_status = False
        while recv_status is False:
            try:
                self.sock.recv_into(result.buffer,
                                    result.buf_size())
                result.unpack()
                recv_status = True
            except socket.error as err:
                print(err.errno)
                self.connected = False
                print("Attempting to connect...")
                self.reconnect()
                recv_status = False

        return result

    def recv_cmd(self, cmd):
        print('try to recv_cmd')
        try:
            self.response = proto.Header()
            if self.response.buf_size() is not 0:
                self.sock.recv_into(self.response.buffer,
                                    self.response.buf_size())
            self.response.unpack()
            print('got responce cmd', self.response.cmd_num)
            if cmd is not proto.CMD_NUMS['CommitTransaction']:
                if cmd is not self.response.cmd_num:
                    return False

        except Exception as e:
            logging.error(e)

        return True

    def _recv(self, cmd, _type):
        print('try to recv')
        recv_status = False
        while recv_status is False:
            try:
                self.response = proto.Header()
                if self.response.buf_size() is not 0:
                    self.sock.recv_into(self.response.buffer,
                                        self.response.buf_size())
                self.response.unpack()
                print('got responce cmd', self.response.cmd_num)
                if cmd is not proto.CMD_NUMS['CommitTransaction']:
                    if cmd is not self.response.cmd_num:
                        return False

                _s = proto_manager.create_struct(_type)
                if _s is None:
                    return
                self.sock.recv_into(_s.buffer,
                                        _s.buf_size())
                _s.unpack()
                recv_status = True

                resp_block = proto.TerminatingBlock()
                self.sock.recv_into(resp_block.buffer,
                                    resp_block.buf_size())
                resp_block.unpack()

                return _s
            except socket.error as err:
                    recv_status = False
                    print(err.errno)
                    self.connected = False
                    print("Attempting to connect...")
                    self.reconnect()



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
        print('form_cmd', cmd)
        # ok = self.recv_cmd(cmd)
        # print('status', ok)
        # if not ok:
        #    return None
        result = self._recv(cmd, _type)
        # if term_block is True:
        #     self.recv_term_block()

        return result

