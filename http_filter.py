#coding: utf-8

from xsocket import XSocket
from gevent import socket
from http_parser import HTTPRequest, HTTPResponse
from enum import Enum

STATES = Enum("WaitingForRequest", "WaitingForResponse", "Ignore", "HTTP_STEP1")



class HTTPFilter(XSocket):
    def __init__(self, addr):
        super(HTTPFilter, self).__init__(None, addr)
        self.states = STATES.WaitingForRequest
        self.setFilter(False)

    def setFilter(self, val):
        self._filter = val
        
    def recv(self, size):
        data = super(HTTPFilter, self).recv(size)
        if not self._filter: return data

        if self.states == STATES.WaitingForResponse:
            self.parse_response(data)

        return data

    def sendall(self, data):
        ret = super(HTTPFilter, self).send(data)
        if not self._filter: return ret

        if self.states == STATES.WaitingForRequest:
            self.parse_request(data)
        return ret

    def parse_request(self, data):
        if data.startswith('GET '): # is http request!
            header = HTTPRequest(data)
            print header
            url = header.path
            self.states = STATES.WaitingForResponse
            self.cached_objs = {'url': url, 'request-header':header}
        else:
            self.states = STATES.Ignore

    def parse_response(self, data):
        if data.startswith('HTTP'): # is http response!
            header = HTTPResponse(data)
            print header
            self.states = STATES.Ignore # FIXME
        else:
            self.states = STATES.Ignore

