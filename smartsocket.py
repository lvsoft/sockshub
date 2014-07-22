#coding: utf-8
"""
a wrapper for multiple socks5 proxy & http proxy
"""
from xsocket import XSocket
from clients import HTTPProxy, SocksProxy
from functools import partial

clients = [partial(HTTPProxy, ("10.239.120.37", 911)),
           partial(SocksProxy, ("10.7.211.16", 1080)),
           XSocket]

def SmartSocket(addr):
    instance = clients[1]
    return instance(addr)




