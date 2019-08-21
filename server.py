#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socketserver
import traceback
import checksum


# commands for testing server: telnet 59.57.247.184 8105
class MyTCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        count = 0
        while True:
            count += 1
            try:
                # data = self.rfile.readline()
                data = self.request.recv(10240)
                if not data:
                    break
                output = ""
                # data = self.rfile.read(1024)
                for each in data:
                    output = output + "{:0>2x}".format(each) + " "
                #print(output)
                with open(str(self.client_address[1])+"_"+str(count)+"_binlog.txt", "wb+") as f:
                    f.write(data)
                with open(str(self.client_address[1])+"_"+str(count)+"_strlog.txt", "w+") as e:
                    #print("exe")
                    e.write(output)
                # print("data: " + data.hex())
                # print(type(data))

                print('receive from (%r):%s' % (self.client_address, checksum.hex_str(data)))
                msg = checksum.generate_response(data, 0x1)
                self.request.sendall(msg)
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
    HOST, PORT = '172.16.6.21', 8105
    with socketserver.ForkingTCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()
