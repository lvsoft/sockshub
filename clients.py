#coding: utf-8

"""
implementation for various proxy clients
"""

from xsocket import XSocket
from gevent import socket
import struct

def inet_aton(hostip): return struct.unpack("!I", socket.inet_aton(hostip))[0]

class ConnectionException(Exception): pass

class HTTPProxy(XSocket):
    def __init__(self, conf, addr):
        super(HTTPProxy, self).__init__(addr=conf)

        # init http proxy connection
        self.sendall("CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\nAccept: */*\r\nContent-Type: text/html\r\nProxy-Connection: Keep-Alive\r\nContent-length: 0\r\n\r\n".format(host=addr[0], port=addr[1]))

        # recv result
        response = self.recv(20)
        if "200" not in response:
            raise ConnectionException(response.split('\r\n')[0])
        self._wait_head_done = True

    def forward(self, dest):
        if self._wait_head_done:
            while True:
                data = self.recv(1024)
                p = data.find('\r\n\r\n')
                if p>=0:
                    self._wait_head_done = False
                    dest.sendall(data[p+4:])
        super(HTTPProxy, self).forward(dest)

class SocksProxy(XSocket):
    def __init__(self, conf, addr):
        super(SocksProxy, self).__init__(addr=conf)

        # init socks5 connection
        self.pack('!BBB', 0x05, 0x01, 0x00);
        ver, n_method = self.unpack('!BB', 2)
        if n_method == 0xff:
            raise ConnectionException('unsupported socks 5 proxy')
        if n_method != 0x00:
            raise ConnectionException('socks 5 need authentication, which is not supported yet')

        self.pack('!BBBBIH', 0x05, 0x01, 0x00, 0x01, inet_aton(addr[0]), addr[1])
        _,_,_,_, host, port = self.unpack("!BBBBIH", 10)

