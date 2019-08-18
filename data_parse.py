#!/usr/bin/env python
# -*- coding:utf-8 -*-
import struct
import traceback

from utils import check_sum, current_time, extract_data_unit, print_0x, str2hex


# class DataParse(socketserver.StreamRequestHandler):
class DataParse:
    # def __init__(self,data):
    #     pass

    def handle(self):
        while True:
            try:
                # data = self.rfile.readline()
                # data = self.request.recv(1024)
                mybytes = b""
                with open("Real-time_reporting.txt", "r+") as binfile:
                    data = binfile.read()
                    data = data.split(" ")
                    for byte in range(len(data)):
                        mybytes += struct.pack("B", str2hex(data[byte]))

                data = mybytes
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
                if reply != -1 and reply != None:
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

    # 整车数据解析
    @staticmethod
    def location_data_parse(data_unit, marker_len):
        loc_units_length = 9
        loc_status_flag = data_unit[marker_len + 1]
        loc_status = "有效定位" if (loc_status_flag & 0x01) == 0x00 else "无效定位"
        latitude_direction = "北纬" if (loc_status_flag & 0x02) == 0x00 else "南纬"
        longitude_direction = "东经" if (loc_status_flag & 0x04) == 0x00 else "西经"
        latitude_val = (data_unit[marker_len + 2] * 0x1000000 + data_unit[marker_len + 3] * 0x10000
                        + data_unit[marker_len + 4] * 0x100 + data_unit[marker_len + 5]) / 1000000.0
        longitude_val = (data_unit[marker_len + 6] * 0x1000000 + data_unit[marker_len + 7] * 0x10000
                         + data_unit[marker_len + 8] * 0x100 + data_unit[marker_len + 9]) / 1000000.0
        loc_data = latitude_direction + str(latitude_val) + "度, " + longitude_direction + str(longitude_val) + "度"
        latitude_val = str(latitude_val)
        longitude_val = str(longitude_val)
        marker_len += loc_units_length + 1
        return loc_status, loc_data, latitude_val, longitude_val, marker_len

    # 报警数据解析
    @staticmethod
    def caution_data_parse(data_unit, marker_len):
        temp_marker = marker_len + 6
        caution_units_len_1 = 4 * (data_unit[temp_marker])
        temp_marker += caution_units_len_1 + 1
        caution_units_len_2 = 4 * (data_unit[temp_marker])
        temp_marker += caution_units_len_2 + 1
        caution_units_len_3 = 4 * (data_unit[temp_marker])
        temp_marker += caution_units_len_3 + 1
        caution_units_len_4 = 4 * (data_unit[temp_marker])
        caution_units_len = 9 + caution_units_len_1 + caution_units_len_2 + \
                            caution_units_len_3 + caution_units_len_4

        top_caution_level = data_unit[marker_len + 1]
        universal_caution_flag = data_unit[marker_len + 2:marker_len + 6]
        universal_caution_flag = str(universal_caution_flag, 'utf-8')
        marker_len += caution_units_len + 1
        return top_caution_level, universal_caution_flag, marker_len

        pass

    @staticmethod
    def vehicle_position_parse(data_unit, marker_len):
        vehi_status_flag_list = ["启动", "熄火", "其他"]
        vehi_status_flag = data_unit[marker_len + 1]
        vehi_status = vehi_status_flag_list[vehi_status_flag - 1]

        vehi_speed_1 = data_unit[marker_len + 4]
        vehi_speed_2 = data_unit[marker_len + 5]
        if vehi_speed_1 != 0xFF:
            vehi_speed = str((vehi_speed_1 * 0x100 + vehi_speed_2) / 10.0)
        elif vehi_speed_2 == 0xFF:
            vehi_speed = "无效"
        elif vehi_speed_2 == 0xFE:
            vehi_speed = "异常"

        SOC_ = data_unit[marker_len + 14]
        if SOC_ != 0xFF and SOC_ != 0xFE:
            SOC = str(SOC_) + "%"
        elif SOC_ == 0xFF:
            SOC = "无效"
        elif SOC_ == 0xFE:
            SOC = "异常"
        marker_len += 21
        return vehi_status, vehi_speed, SOC, marker_len

    @staticmethod
    def process_message(data):
        # print("原始数据: ", binascii.b2a_hex(data))
        if data[0] != 0x23 or data[1] != 0x23:
            print("首字节非2323!")
            return -1

        # 提取数据单元
        data_unit = extract_data_unit(data)

        # 比较校验码
        [checkres, check_code] = check_sum(data, True)
        if checkres != 0x00:
            print("校验失败！")
            return -1

        # 提取车辆VIN码
        VIN = data[4:20]
        print("VIN: ", VIN)
        print_0x(VIN)
        print("\n")

        # 提取加密方式
        encode_type = data[21]
        if encode_type == 0x01:
            print("无加密")
            # to do

        # 处理应答位
        if data[3] == 0xFE:
            print("此包为命令包,需要应答！")
            # to do
        else:
            print("此包不需要应答")
            # to do

        # 处理标识位
        if data[2] == 0x01:
            print("车辆登入!")

            # 创建数据字典，调用数据库API进行存储
            DataParse.data_store_to_hbase(data)

            # 处理应答位
            if data[3] == 0xFE:
                print("此包为命令包,需要应答！")
                reply = DataParse.get_vehicle_register_reply(data)
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
            # 创建数据字典，调用数据库API进行存储
            DataParse.data_store_to_hbase(data)

            # 处理应答位
            if data[3] == 0xFE:
                print("此包为命令包,需要应答！")
                # to do
            else:
                print("此包不需要应答")
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

    @staticmethod
    def get_vehicle_register_reply(data):  # 应答数据(应答位替换, 时间替换, 校验位替换)
        time_now = current_time()
        data = bytearray(data)
        print("before:")
        print_0x(data)
        [checkres, _] = check_sum(data)
        if checkres == 0x00:
            data[3] = 0x01
        else:
            print("数据校验错误！")
            return -1

        data[22] = time_now[0] % 2000
        data[23] = time_now[1]
        data[24] = time_now[2]
        data[25] = time_now[3]
        data[26] = time_now[4]
        data[27] = time_now[5]
        [_, check_code] = check_sum(data)
        data[-1] = check_code
        vehicle_register_reply = bytes(data)
        # print("车辆登入应答数据:")
        # print_0x(vehicle_register_reply)
        return vehicle_register_reply

    @staticmethod
    def data_store_to_hbase(data):
        # ------------------------------ 通用数据 -------------------------------------------
        # 原始数据data
        # 提取车辆VIN码
        VIN = data[4:20]
        # 数据单元
        data_unit, data_unit_length = extract_data_unit(data)
        print_0x(data_unit)
        # 数据类型：车辆登入、实时信息上报、心跳
        a = data[2]
        data_flag_list = ["车辆登入", "实时信息上报", "补发信息上报", "车辆登出", "平台登入",
                          "平台登出", "终端数据预留（上行）", "上行数据系统预留", "终端数据预留（下行）",
                          "下行数据系统预留", "平台自定义数据", "命令标识无法识别!"]
        flag = process_flag(data)
        flag_ = data_flag_list[flag]
        # ----------------------------- 分类数据 --------------------------------------------
        # 实时信息上报
        # data collection time
        data_collection_time = data_unit[0:6]
        data_collection_time = bytes_time_to_fmt_time(data_collection_time)
        marker_len = 6
        while marker_len < data_unit_length:
            data_type = data_unit[marker_len]
            data_type_2 = data_unit[marker_len + 1]
            if data_type == 0x01:  # 整车数据
                print("整车数据起始点： ", marker_len)
                vehi_status, vehi_speed, SOC, marker_len = DataParse.vehicle_position_parse(data_unit, marker_len)

            elif data_type == 0x02:  # 驱动电机数据, to do
                print("驱动电机数据起始点： ", marker_len)
                drive_motor_num = data_unit[marker_len + 1]
                drive_motor_units_len = drive_motor_num * 12
                marker_len += drive_motor_units_len + 2

            elif data_type == 0x03:  # 燃料电池
                print("燃料电池数据起始点： ", marker_len)
                temperature_probe_num_1 = data_unit[marker_len + 7]
                temperature_probe_num_2 = data_unit[marker_len + 8]
                fuel_units_len = 18 + temperature_probe_num_1 * 0x100 + temperature_probe_num_2
                marker_len += fuel_units_len + 1

            elif data_type == 0x04:  # 发动机数据
                print("发动机数据起始点： ", marker_len)
                engine_units_len = 5
                marker_len += engine_units_len + 1

            elif data_type == 0x05:  # 车辆位置数据
                print("位置数据起始点： ", marker_len)
                loc_status, loc_data, latitude_val, longitude_val, marker_len \
                    = DataParse.location_data_parse(data_unit, marker_len)

            elif data_type == 0x06:  # 极值数据
                print("极值数据起始点： ", marker_len)
                extremum_units_len = 14
                marker_len += extremum_units_len + 1

            elif data_type == 0x07:  # 报警数据
                print("报警数据起始点： ", marker_len)
                top_caution_level, universal_caution_flag, marker_len = \
                    DataParse.caution_data_parse(data_unit, marker_len)

            elif data_type == 0x08:  # 可充电储能装置电压数据
                print("可充电储能装置电压数据起始点： ", marker_len)
                # 可充电设备个数默认为1
                recharge_vol_sys_num = data_unit[marker_len+1]
                vol_unit_cell_num = data_unit[marker_len+11]
                recharge_vol_sys_units_len = 2*vol_unit_cell_num + 11
                marker_len += recharge_vol_sys_units_len + 1

            elif data_type == 0x09:  # 可充电储能装置温度数据
                print("可充电储能装置温度数据起始点： ", marker_len)
                # 可充电设备个数默认为1
                recharge_tem_sys_num = data_unit[marker_len+1]
                tem_probe_num_1 = data_unit[marker_len+3]
                tem_probe_num_2 = data_unit[marker_len+4]
                tem_probe_num = tem_probe_num_1*0x100 + tem_probe_num_2
                recharge_tem_sys_units_len = 3 + tem_probe_num
                marker_len += recharge_tem_sys_units_len + 1

            elif data_type<=0x7F and data_type>=0x30:

                print("读取结束!预留数据起始点： ", marker_len)
                break
        print("数据读取完成！")
        input()


def bytes_time_to_fmt_time(time_bytes):
    fmt_time = "20" + str(time_bytes[0]) + "年" + str(time_bytes[1]) + "月" + str(time_bytes[2]) + "日" \
               + str(time_bytes[3]) + "时" + str(time_bytes[4]) + "分" + str(time_bytes[5]) + "秒"
    return fmt_time


def process_flag(data):
    # 处理标识位
    if data[2] == 0x01:
        print("车辆登入!")
        return 0
    elif data[2] == 0x02:
        print("实时信息上报数据")
        return 1
    elif data[2] == 0x03:
        print("补发信息上报")
        return 2
    elif data[2] == 0x04:
        print("车辆登出")
        return 3
    elif data[2] == 0x05:
        print("平台登入")
        return 4
    elif data[2] == 0x06:
        print("平台登出")
        return 5
    elif data[2] <= 0x08 & data[2] >= 0x07:
        print("终端数据预留（上行）")
        return 6
    elif data[2] <= 0x7F & data[2] >= 0x09:
        print("上行数据系统预留")
        return 7
    elif data[2] <= 0x82 & data[2] >= 0x80:
        print("终端数据预留（下行）")
        return 8
    elif data[2] <= 0x82 & data[2] >= 0x80:
        print("下行数据系统预留")
        return 9
    elif data[2] <= 0xFE & data[2] >= 0xC0:
        print("平台自定义数据")
        return 10
    else:
        print("命令标识无法识别!")
        return 11


if __name__ == '__main__':
    # HOST, PORT = 'localhost', 8105
    # with socketserver.ForkingTCPServer((HOST, PORT), DataParse) as server:
    #     server.serve_forever()
    test_object = DataParse()
    test_object.handle()
