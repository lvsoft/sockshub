#coding: utf-8
from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO

class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message

    def __str__(self):
        if self.error_code: return "<error:%d, %s>" % (self.error_code, self.error_message)
        return "<%s: %s>" % (self.command, self.path) + "\n".join(["->   %s:%s" % (x[0], x[1]) for x in self.headers.items()])
    __repr__ = __str__

class HTTPResponse(HTTPRequest):
    def parse_request(self):
        """Parse a request (internal).

        The request should be stored in self.raw_requestline; the results
        are in self.command, self.path, self.request_version and
        self.headers.

        Return True for success, False for failure; on failure, an
        error is sent back.

        """
        self.command = None  # set in case of error on the first line
        self.request_version = version = self.default_request_version
        self.close_connection = 1
        requestline = self.raw_requestline
        requestline = requestline.rstrip('\r\n')
        self.requestline = requestline
        words = requestline.split(' ', 2)

#        import ipdb; ipdb.set_trace()
        if len(words) == 3:
            version, code, code_str = words
            code = int(code)
            if version[:5] != 'HTTP/':
                self.send_error(400, "Bad request version (%r)" % version)
                return False
            try:
                base_version_number = version.split('/', 1)[1]
                version_number = base_version_number.split(".")
                # RFC 2145 section 3.1 says there can be only one "." and
                #   - major and minor numbers MUST be treated as
                #      separate integers;
                #   - HTTP/2.4 is a lower version than HTTP/2.13, which in
                #      turn is lower than HTTP/12.3;
                #   - Leading zeros MUST be ignored by recipients.
                if len(version_number) != 2:
                    raise ValueError
                version_number = int(version_number[0]), int(version_number[1])
            except (ValueError, IndexError):
                self.send_error(400, "Bad response version (%r)" % version)
                return False
            if version_number >= (1, 1) and self.protocol_version >= "HTTP/1.1":
                self.close_connection = 0
            if version_number >= (2, 0):
                self.send_error(505,
                          "Invalid HTTP Version (%s)" % base_version_number)
                return False
        else:
            self.send_error(400, "Bad response syntax (%r)" % requestline)
            return False
        self.response_version, self.response_code, self.response_code_str = version, code, code_str

        # Examine the headers and look for a Connection directive
        self.headers = self.MessageClass(self.rfile, 0)

        conntype = self.headers.get('Connection', "")
        if conntype.lower() == 'close':
            self.close_connection = 1
        elif (conntype.lower() == 'keep-alive' and
              self.protocol_version >= "HTTP/1.1"):
            self.close_connection = 0
        return True

    def __str__(self):
        if self.error_code: return "<error:%d, %s>" % (self.error_code, self.error_message)
        return "<%d: %s>" % (self.response_code, self.response_code_str) + "\n".join(["<-   %s:%s" % (x[0], x[1]) for x in self.headers.items()])
    __repr__ = __str__
