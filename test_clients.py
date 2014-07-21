from clients import SocksProxy, HTTPProxy

def test_socks_proxy():
    s = SocksProxy(("127.0.0.1", 3125), ("192.168.1.20", 80))
    s.sendall("GET /\r\n\r\n")
    data = s.recv(4096)
    print data

def test_http_proxy():
    s = HTTPProxy(("127.0.0.1", 8080), ("192.168.1.20", 80))
    s.sendall("GET /\r\n\r\n")
    data = s.recv(4096)
    print data

if __name__=="__main__":
    #    test_socks_proxy()
    test_http_proxy()