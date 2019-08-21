#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socket
import struct
import threading
from utils import print_0x, str2hex
import data_parse
# import checksum
import time


def client():
    HOST = 'localhost'
    PORT = 8105
    # with open("29545_10_binlog.txt", "rb+") as binfile:
    #     data = binfile.read()

    mybytes = b""
    with open("heartbeat.txt", "r+") as binfile:
        data = binfile.read()
        data = data.split(" ")
        for byte in range(len(data)):
            mybytes += struct.pack("B", str2hex(data[byte]))
    data = mybytes

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(data)
        #time.sleep(5)
        #s.sendall(b'')
        print("send data:")
        print_0x(data)
        data = s.recv(10240)

        print("recieve data:")
        print_0x(data)
        input()
        #time.sleep(5)
        #s.shutdown(2)
        #time.sleep(5)


def main():
    for i in range(0, 1):
        t = threading.Thread(target=client)
        t.start()


if __name__ == '__main__':
    main()