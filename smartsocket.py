#coding: utf-8
"""
a wrapper for multiple socks5 proxy & http proxy
"""
from xsocket import XSocket
from clients import HTTPProxy, SocksProxy
from functools import partial

clients = [partial(HTTPProxy, ("127.0.0.1", 8080)),
           partial(SocksProxy, ("127.0.0.1", 3125))]

class SmartSocket(XSocket):
    def forward(self, dest):
        try:
            while True:
                data = self.recv(1024)
                if not data:
                    break
                dest.sendall(data)
        finally:
            self.close()
            dest.close()
