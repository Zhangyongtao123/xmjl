
import time


def check_sum(data, print_res=False):       # to do ：计算校验位
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
    if print_res:
        print("checksum: " + "{:0>2x}".format(checksum))
        print("checkres: " + "{:0>2x}".format(checkres))
    return [checkres, checksum]


def current_time():                         # 计算当前时间
    # 获取当前时间 格式：%Y.%m.%d %H:%M:%S
    ori_time = time.localtime(time.time())
    time_now = [ori_time.tm_year, ori_time.tm_mon, ori_time.tm_mday, ori_time.tm_hour,
                ori_time.tm_min, ori_time.tm_sec]
    return time_now


def extract_data_unit(data, print_result=True):    # 提取数据单元
    # 获取数据单元长度
    data_unit_length = data[22] * 256 + data[23]

    # 提取数据单元
    end_position = 24 + data_unit_length
    data_unit = data[24:end_position]
    if print_result:
        print("数据总长度（字节）： ", len(data))
        print("数据单元长度（字节）： ", data_unit_length)
        print("数据单元：")
        print_0x(data_unit)
    return data_unit, data_unit_length


def print_0x(data, show_result=True, NO_id=True):       # 转码显示
    output = ""
    if NO_id:
        for each in data:
            # print(each)
            output = output + "{:0>2x}".format(each) + " "
    else:
        for idx, each in enumerate(data):
            # print(each)
            output += str(idx) + ":" + "{:0>2x}".format(each) + " "
    if show_result:
        print(output)
    return output


def str2hex(s):
    odata = 0;
    su =s.upper()
    for c in su:
        tmp=ord(c)
        if tmp <= ord('9') :
            odata = odata << 4
            odata += tmp - ord('0')
        elif ord('A') <= tmp <= ord('F'):
            odata = odata << 4
            odata += tmp - ord('A') + 10
    return odata


def bytes_time_to_fmt_time(time_bytes):
    fmt_time = "20" + str(time_bytes[0]) + "-" + str(time_bytes[1]) + "-" + str(time_bytes[2]) + " " \
               + str(time_bytes[3]) + ":" + str(time_bytes[4]) + ":" + str(time_bytes[5])
    return fmt_time


def process_flag(data):
    # 处理标识位
    if data[2] == 0x01:
        # print("车辆登入!")
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
