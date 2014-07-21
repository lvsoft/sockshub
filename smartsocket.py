#coding: utf-8
"""
a wrapper for multiple socks5 proxy & http proxy
"""
from xsocket import XSocket

class SmartSocket(HTTPProxy):
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
