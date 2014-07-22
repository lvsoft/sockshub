#coding: utf-8

import gevent
import struct
from gevent import socket

class XSocket(gevent.socket.socket):
    def __init__(self, socket = None, addr = None):
        if socket is not None:
            gevent.socket.socket.__init__(self, _sock = socket)
        elif addr is not None:
            gevent.socket.socket.__init__(self)
            self.connect(addr)
        else:
            raise Exception("%s.init: bad arguments", self.__class__)

    def unpack(self, fmt, length):
        data = self.recv(length)
        if len(data) < length:
            raise Exception("XSocket.unpack: bad formatted stream")
        return struct.unpack(fmt, data)

    def pack(self, fmt, *args):
        data = struct.pack(fmt, *args)
        return self.sendall(data)

    def forward(self, dest):
        try:
            while True:
                data = self.recv(1400)
                if not data:
                    break
                dest.sendall(data)
        except socket.error:
            pass
        finally:
            self.close()
            dest.close()
