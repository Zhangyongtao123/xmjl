#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socketserver
import binascii
import time
import traceback


# class DataParse(socketserver.StreamRequestHandler):

class DataParse:
    # def __init__(self,data):
    #     pass

    def handle(self):
        while True:
            try:
                # data = self.rfile.readline()
                # data = self.request.recv(1024)
                with open("virtuallog.txt", "rb+") as binfile:
                    data = binfile.read()
                if not data:
                    break
                print("原始数据：")
                output = print_0x(data)

                reply = self.process_message(data)
                if reply == -1:
                    print("出错！")
                with open("binlog.txt", "wb+") as f:
                    f.write(data)
                with open("strlog.txt", "w+") as e:
                    e.write(output)
                # print("data: " + data.hex())
                # print(type(data))
                print("vehicle_register_reply:")
                print_0x(reply)
                input()
                print('receive from (%r):%r' % (self.client_address, output))
                self.request.sendall(reply)
            except:
                traceback.print_exc()
                break

    # 判断所收到数据开头是2323

    # 解析时间戳
    @staticmethod
    def timestamp_parse():
        pass

    # 整车数据解析
    @staticmethod
    def vehicle_data_parse(self):
        pass

    # 报警数据解析
    @staticmethod
    def caution_data_parse(self):
        pass

    @staticmethod
    def vehicle_position_parse(self):
        pass

    @staticmethod
    def process_message(data):
        # print("原始数据: ", binascii.b2a_hex(data))
        if data[0] != 0x23 or data[1] != 0x23:
            print("首字节非2323!")
            return -1

        # 提取数据单元
        data_unit = extract_data_unit(data)

        # 比较校验码
        [checkres, check_code] = check_sum(data)
        if checkres != 0x00:
            print("校验失败！")
            return -1

        # 提取车辆VIN码
        VIN = data[4:20]
        print("VIN: ", VIN)
        print_0x(VIN)

        # 提取加密方式
        encode_type = data[21]
        if encode_type == 0x01:
            print("无加密")
            # to do


        # 处理标识位
        if data[2] == 0x01:
            print("车辆登入!")
            # 处理应答位
            if data[3] == 0xFE:
                print("此包为命令包,需要应答！")
                reply = get_vehicle_register_reply(data)
                return reply
                # to do
            else:
                print("此包不需要应答")
                return 0
                # to do

            # 应答
            # to do
        elif data[2] == 0x02:
            print("实时信息上报数据")
            # to do
        elif data[2] == 0x03:
            print("补发信息上报")
            # to do
        elif data[2] == 0x04:
            print("车辆登出")
            # to do
        elif data[2] == 0x05:
            print("平台登入")
            # to do
        elif data[2] == 0x06:
            print("平台登出")
            # to do
        elif data[2] == 0x03:
            print("车辆登出")
            # to do
        elif data[2] <= 0x08 & data[2] >= 0x07:
            print("终端数据预留（上行）")
            # to do
        elif data[2] <= 0x7F & data[2] >= 0x09:
            print("上行数据系统预留")
            # to do
        # elif data[2] <= 0x82 & data[2] >= 0x80:
        #     print("终端数据预留（下行）")
        #     # to do
        # elif data[2] <= 0x82 & data[2] >= 0x80:
        #     print("下行数据系统预留")
        #     # to do
        elif data[2] <= 0xFE & data[2] >= 0xC0:
            print("平台自定义数据")
            # to do
        else:
            print("命令标识无法识别!")
            return -1




# 应答数据(应答位替换, 时间替换, 校验位替换)
def get_vehicle_register_reply(data):
    time_now = current_time()
    print("替换前的数据： ", data)
    print("替换前的数据类型： ", type(data))
    data = bytearray(data)
    print("before:")
    print_0x(data)
    data[3] = 0x02
    data[22] = time_now[0] % 2000
    data[23] = time_now[1]
    data[24] = time_now[2]
    data[25] = time_now[3]
    data[26] = time_now[4]
    data[27] = time_now[5]
    [_, check_code] = check_sum(data)
    data[-1] = check_code
    vehicle_register_reply = bytes(data)
    print("after:")
    print_0x(vehicle_register_reply)
    return vehicle_register_reply


# 转码显示
def print_0x(data, show_result=True):
    output = ""
    for each in data:
        output = output + "{:0>2x}".format(each) + " "
    if show_result:
        print(output)
    return output


# 提取数据单元
def extract_data_unit(data):
    # 获取数据单元长度
    print("数据长度： ", len(data))
    data_unit_length = data[22] * 256 + data[23]
    print("数据单元长度： ", data_unit_length)

    # 提取数据单元
    end_position = 24 + data_unit_length
    data_unit = data[24:end_position]
    print("数据单元：")
    print_0x(data_unit)
    return data_unit


# 计算当前时间
def current_time():
    # 获取当前时间 格式：%Y.%m.%d %H:%M:%S
    ori_time = time.localtime(time.time())
    time_now = [ori_time.tm_year, ori_time.tm_mon, ori_time.tm_mday, ori_time.tm_hour,
                ori_time.tm_min, ori_time.tm_sec]
    return time_now


# to do ：计算校验位
def check_sum(data):
    # with open("binlog.txt", "rb+") as binfile:
    #     data = binfile.read()
    checkres = 0

    output = ""
    for each in data:
        output = output + "{:0>2x}".format(each) + " "
        checkres = checkres ^ each
    size = len(data)
    checksum = 0
    for i in range(0, size - 1):
        checksum = checksum ^ data[i]
    print("checksum: " + "{:0>2x}".format(checksum))
    print("checkres: " + "{:0>2x}".format(checkres))
    return [checkres, checksum]

if __name__ == '__main__':
    # HOST, PORT = 'localhost', 8105
    # with socketserver.ForkingTCPServer((HOST, PORT), DataParse) as server:
    #     server.serve_forever()
    test_object = DataParse()
    test_object.handle()
