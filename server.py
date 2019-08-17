#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socketserver
import traceback


# commands for testing server: telnet 59.57.247.184 8105
class MyTCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        while True:
            try:
                #data = self.rfile.readline()
                data = self.request.recv(1024)
                if not data:
                    break
                output = ""
                #data = self.rfile.read(1024)
                for each in data:
                    output = output + "{:0>2x}".format(each) + " "
                print(output)
                with open("binlog.txt", "wb+") as f:
                    f.write(data)
                with open("strlog.txt", "w+") as e:
                    print("exe")
                    e.write(output)
                #print("data: " + data.hex())
                #print(type(data))


                print('receive from (%r):%r' % (self.client_address, data))
                self.request.sendall(data.upper())
            except:
                traceback.print_exc()
                break


        '''
        try:
            data = self.request.recv(40)
            print('receive from (%r):%r' % (self.client_address, data))
        except:
            traceback.print_exc()
        '''


if __name__ == '__main__':
    HOST, PORT = 'localhost', 8105
    with socketserver.ForkingTCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()
