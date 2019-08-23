#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socketserver
import json
import traceback

import requests

from utils import check_sum, current_time, extract_data_unit, print_0x, bytes_time_to_fmt_time, process_flag


class DataParse(socketserver.StreamRequestHandler):
    # class DataParse:
    # def __init__(self,data):
    #     pass

    def handle(self):
        count = 0
        while True:
            count += 1
            try:
                # data = self.rfile.readline()
                data = self.request.recv(10240)
                # mybytes = b""
                # with open("Real-time_reporting.txt", "r+") as binfile:
                #     data = binfile.read()
                #     data = data.split(" ")
                #     for byte in range(len(data)):
                #         mybytes += struct.pack("B", str2hex(data[byte]))

                # data = mybytes
                if not data:
                    break
                output = print_0x(data, False)
                print('\n收到数据(%r):' % (self.client_address,))
                print(output)

                reply = self.process_message(data)
                if reply == -1:
                    print("出错！")
                # with open(str(self.client_address[1]) + "_" + str(count) + "_binlog.txt", "wb+") as f:
                #    f.write(data)
                # with open(str(self.client_address[1]) + "_" + str(count) + "_strlog.txt", "w+") as e:
                # print("exe")
                #    e.write(output)
                # with open("binlog.txt", "wb+") as f:
                #     f.write(data)
                # with open("strlog.txt", "w+") as e:
                #     e.write(output)
                # print("data: " + data.hex())
                # print(type(data))
                print("应答数据:")
                if reply != -1 and reply != None and reply != 0:
                    print_0x(reply)
                    self.request.sendall(reply)

            except:
                traceback.print_exc()
                break

    # 判断所收到数据开头是2323

    # 解析时间戳
    @staticmethod
    def timestamp_parse():
        pass

    # 整车position数据解析
    @staticmethod
    def location_data_parse(data_unit, marker_len):
        loc_units_length = 9
        loc_status_flag = data_unit[marker_len + 1]
        loc_status = "valid_loc" if (loc_status_flag & 0x01) == 0x00 else "invalid_loc"
        latitude_direction = "north" if (loc_status_flag & 0x02) == 0x00 else "south"
        longitude_direction = "east" if (loc_status_flag & 0x04) == 0x00 else "west"
        latitude_val = (data_unit[marker_len + 2] * 0x1000000 + data_unit[marker_len + 3] * 0x10000
                        + data_unit[marker_len + 4] * 0x100 + data_unit[marker_len + 5]) / 1000000.0
        longitude_val = (data_unit[marker_len + 6] * 0x1000000 + data_unit[marker_len + 7] * 0x10000
                         + data_unit[marker_len + 8] * 0x100 + data_unit[marker_len + 9]) / 1000000.0
        # loc_data = latitude_direction + str(latitude_val) + "度, " + longitude_direction + str(longitude_val) + "度"
        latitude_val = str(latitude_val)
        longitude_val = str(longitude_val)
        marker_len += loc_units_length + 1
        return loc_status, latitude_direction, longitude_direction, latitude_val, longitude_val, marker_len

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

        top_caution_level = str(data_unit[marker_len + 1])
        universal_caution_flag = data_unit[marker_len + 2:marker_len + 6]
        universal_caution_flag = str(universal_caution_flag)
        marker_len += caution_units_len + 1
        return top_caution_level, universal_caution_flag, marker_len

        pass

    # 整车数据解析
    @staticmethod
    def vehicle_data_parse(data_unit, marker_len):
        vehi_status_flag_list = ["on", "off", "other"]
        vehi_status_flag = data_unit[marker_len + 1]
        vehi_status = vehi_status_flag_list[vehi_status_flag - 1]

        vehi_speed_1 = data_unit[marker_len + 4]
        vehi_speed_2 = data_unit[marker_len + 5]
        if vehi_speed_1 != 0xFF:
            vehi_speed = str((vehi_speed_1 * 0x100 + vehi_speed_2) / 10.0)
        elif vehi_speed_2 == 0xFF:
            vehi_speed = "invalid"
        elif vehi_speed_2 == 0xFE:
            vehi_speed = "abnormal"

        SOC_ = data_unit[marker_len + 14]
        if SOC_ != 0xFF and SOC_ != 0xFE:
            SOC = str(SOC_) + "%"
        elif SOC_ == 0xFF:
            SOC = "invalid"
        elif SOC_ == 0xFE:
            SOC = "abnormal"
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

        # 提取加密方式
        encode_type = data[21]
        if encode_type == 0x01:
            print("加密方式： 无加密")
            # to do

        # 处理标识位
        if data[2] == 0x01:
            print("命令标识： 车辆登入!")
            # 处理应答位
            if data[3] == 0xFE:
                print("是否应答： 需要应答！")
                reply = DataParse.get_vehicle_register_reply(data)
                return reply
            else:
                print("是否应答： 不需要应答")
        elif data[2] == 0x02:
            print("命令标识： 实时信息上报数据")
            DataParse.data_store_to_hbase(data)
            # 处理应答位
            if data[3] == 0xFE:
                print("是否应答： 需要应答！")
                reply = DataParse.get_vehicle_register_reply(data)
                return reply
            else:
                print("是否应答： 不需要应答")
        elif data[2] == 0x03:
            print("命令标识： 补发信息上报")
            # 处理应答位
            if data[3] == 0xFE:
                print("是否应答： 需要应答！")
                reply = DataParse.get_vehicle_register_reply(data)
                return reply
            else:
                print("是否应答： 不需要应答")
        elif data[2] == 0x04:
            print("命令标识： 车辆登出")
            # 处理应答位
            if data[3] == 0xFE:
                print("是否应答： 需要应答！应答未定！")
            else:
                print("是否应答： 不需要应答")
        elif data[2] == 0x05:
            print("命令标识： 平台登入")
            if data[3] == 0xFE:
                print("是否应答： 需要应答！应答未定！")
            else:
                print("是否应答： 不需要应答")
        elif data[2] == 0x06:
            print("命令标识： 平台登出")
        elif data[2] == 0x07:
            print("命令标识： 心跳")
            # 处理应答位
            if data[3] == 0xFE:
                print("是否应答： 需要应答！")
                reply = DataParse.get_heartbeat_reply(data)
                return reply
            else:
                print("是否应答： 不需要应答")
        elif data[2] == 0x08:
            print("命令标识： 终端校时")
            # 处理应答位
            if data[3] == 0xFE:
                print("此包为命令包,需要应答！")
                reply = DataParse.get_cali_time_reply(data)
                return reply
            else:
                print("此包不需要应答")
        elif data[2] <= 0x7F & data[2] >= 0x09:
            print("命令标识： 上行数据系统预留")
            # 处理应答位
            if data[3] == 0xFE:
                print("是否应答： 需要应答！应答未定！")
                # reply = DataParse.get_vehicle_register_reply(data)
            else:
                print("是否应答： 不需要应答")
        elif data[2] == 0x80:
            print("命令标识： 查询命令")
            # 处理应答位
            if data[3] == 0xFE:
                print("是否应答： 需要应答！应答未定！")
                # reply = DataParse.get_vehicle_register_reply(data)
            else:
                print("是否应答： 不需要应答")
        elif data[2] == 0x81:
            print("命令标识： 设置命令")
            # 处理应答位
            if data[3] == 0xFE:
                print("是否应答： 需要应答！应答未定！")
                # reply = DataParse.get_vehicle_register_reply(data)
            else:
                print("是否应答： 不需要应答")
        elif data[2] == 0x82:
            print("命令标识： 车载终端控制命令")
            if data[3] == 0xFE:
                print("是否应答： 需要应答！应答未定！")
                # reply = DataParse.get_vehicle_register_reply(data)
            else:
                print("是否应答： 不需要应答")
        elif data[2] <= 0xBE & data[2] >= 0x83:
            print("命令标识： 平台自定义数据")
            # 处理应答位
            if data[3] == 0xFE:
                print("是否应答： 需要应答！应答未定！")
                # reply = DataParse.get_vehicle_register_reply(data)
            else:
                print("是否应答： 不需要应答")
        elif data[2] <= 0xFE & data[2] >= 0xC0:
            print("命令标识： 平台自定义数据")
            # 处理应答位
            if data[3] == 0xFE:
                print("是否应答： 需要应答！应答未定！")
                # reply = DataParse.get_vehicle_register_reply(data)
            else:
                print("是否应答： 不需要应答")
        else:
            print("命令标识： 命令标识无法识别!")
            # 处理应答位
            if data[3] == 0xFE:
                print("是否应答： 需要应答！应答未定！")
                # reply = DataParse.get_vehicle_register_reply(data)
            else:
                print("是否应答： 不需要应答")
        return 0

    @staticmethod
    def get_vehicle_register_reply(data):  # 应答数据(应答位替换, 时间替换, 校验位替换)
        time_now = current_time()
        data = bytearray(data)
        [checkres, _] = check_sum(data)
        if checkres == 0x00:
            data[3] = 0x01
        else:
            print("数据校验错误！")
            return -1
        data[24] = time_now[0] % 2000
        data[25] = time_now[1]
        data[26] = time_now[2]
        data[27] = time_now[3]
        data[28] = time_now[4]
        data[29] = time_now[5]
        [_, check_code] = check_sum(data)
        data[-1] = check_code
        vehicle_register_reply = bytes(data)
        # print("车辆登入应答数据:")
        # print_0x(vehicle_register_reply)
        return vehicle_register_reply

    @staticmethod
    def get_heartbeat_reply(data):  #
        data = bytearray(data)
        print("ori_data:")
        print_0x(data, show_result=True, NO_id=False)
        [checkres, _] = check_sum(data)
        if checkres == 0x00:
            data[3] = 0x01
        else:
            print("数据校验错误！")
            return -1
        [_, check_code] = check_sum(data)
        data[-1] = check_code
        heartbeat_reply = bytes(data)
        # print("车辆登入应答数据:")
        # print_0x(vehicle_register_reply)
        return heartbeat_reply

    @staticmethod
    def get_cali_time_reply(data):  # 应答数据(应答位替换, 时间替换, 校验位替换)
        time_now = current_time()
        data = bytearray(data)
        print("ori_data:")
        print_0x(data)
        [checkres, _] = check_sum(data)
        if checkres == 0x00:
            data[3] = 0x01
        else:
            print("数据校验错误！")
            return -1
        data[24] = time_now[0] % 2000
        data.append(time_now[1])
        data.append(time_now[2])
        data.append(time_now[3])
        data.append(time_now[4])
        data.append(time_now[5])
        [_, check_code] = check_sum(data)
        data.append(check_code)
        vehicle_cali_time_reply = bytes(data)
        # print("车辆登入应答数据:")
        # print_0x(vehicle_register_reply)
        return vehicle_cali_time_reply

    @staticmethod
    def data_store_to_hbase(data):
        # ------------------------------ 通用数据 -------------------------------------------
        # 原始数据data
        # 提取车辆VIN码
        VIN = data[4:20]
        VIN = str(VIN)
        # 数据单元
        data_unit, data_unit_length = extract_data_unit(data, False)
        # 数据类型：车辆登入、实时信息上报、心跳
        data_flag_list = ["车辆登入", "realtime_upload ", "supplementary_upload", "车辆登出", "平台登入",
                          "平台登出", "终端数据预留（上行）", "上行数据系统预留", "终端数据预留（下行）",
                          "下行数据系统预留", "平台自定义数据", "命令标识无法识别!"]
        flag = process_flag(data)
        upload_type = data_flag_list[flag]
        # ----------------------------- 分类数据 --------------------------------------------
        # 实时信息上报
        # data collection time
        data_collection_time = data_unit[0:6]
        data_collection_time = bytes_time_to_fmt_time(data_collection_time)
        marker_len = 6
        vehi_status = None
        vehi_speed = None
        SOC = None
        loc_status = None
        latitude_direction = None
        longitude_direction = None
        # loc_data = None
        latitude_val = None
        longitude_val = None
        top_caution_level = None
        universal_caution_flag = None

        while marker_len < data_unit_length:
            data_type = data_unit[marker_len]
            if data_type == 0x01:  # 整车数据
                print("整车数据起始点： ", marker_len)
                vehi_status, vehi_speed, SOC, marker_len = DataParse.vehicle_data_parse(data_unit, marker_len)

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
                loc_status, latitude_direction, longitude_direction, latitude_val, longitude_val, marker_len \
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
                recharge_vol_sys_num = data_unit[marker_len + 1]
                vol_unit_cell_num = data_unit[marker_len + 11]
                recharge_vol_sys_units_len = 2 * vol_unit_cell_num + 11
                marker_len += recharge_vol_sys_units_len + 1

            elif data_type == 0x09:  # 可充电储能装置温度数据
                print("可充电储能装置温度数据起始点： ", marker_len)
                # 可充电设备个数默认为1
                recharge_tem_sys_num = data_unit[marker_len + 1]
                tem_probe_num_1 = data_unit[marker_len + 3]
                tem_probe_num_2 = data_unit[marker_len + 4]
                tem_probe_num = tem_probe_num_1 * 0x100 + tem_probe_num_2
                recharge_tem_sys_units_len = 3 + tem_probe_num
                marker_len += recharge_tem_sys_units_len + 1

            elif data_type <= 0x2F and data_type >= 0x0A:
                print("平台交换协议数据，数据类型码： ", data_type)
                break
            elif data_type <= 0x7F and data_type >= 0x30:
                print("预留数据，数据类型码： ", data_type)
                break
            elif data_type <= 0xFE and data_type >= 0x80:
                print("用户自定义数据，数据类型码： ", data_type)
                break
            else:
                print("无法识别数据类型！数据类型码：", data_type)
                break
        print("数据读取完成！")
        json_store_data_ = [{"VIN": VIN, "upload_type": upload_type, "time": data_collection_time,
                             "vehi_status": vehi_status, "vehi_speed": vehi_speed, "SOC": SOC, "loc_status": loc_status,
                             "latitude_direction": latitude_direction, "longitude_direction": longitude_direction,
                             "lati_val": latitude_val, "longi_val": longitude_val, "caution_level": top_caution_level,
                             "caution_flag": universal_caution_flag, "ori_data": str(data)
                             }]
        json_store_data = json.dumps(json_store_data_, indent=4, separators=(',', ': '))
        print("保存数据：")
        print(json_store_data)
        with open("Json_data.txt", "a+") as logfile:
            logfile.write(json_store_data + '\n')
        # headers中添加上content-type这个参数，指定为json格式
        headers = {'Content-Type': 'application/json'}

        try:
            # post的时候，将data字典形式的参数用json包转换成json格式
            response = requests.post(url='http://localhost:5000', headers=headers, data=json_store_data)
            print("response: ", response)
        except requests.exceptions.ConnectionError:
            print("传输异常！本地http服务端未开启")


if __name__ == '__main__':
    HOST, PORT = '0.0.0.0', 8105
    with socketserver.ForkingTCPServer((HOST, PORT), DataParse) as server:
        server.serve_forever()
    # test_object = DataParse()
    # test_object.handle()
