#!/usr/bin/env python3
import socket, time
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    s.bind(('127.0.0.1', 5000))
    s.listen(1)
    print('Bound OK; holding for 10s')
    time.sleep(10)
    s.close()
    print('Released')
except Exception as e:
    print('Bind failed:', repr(e))