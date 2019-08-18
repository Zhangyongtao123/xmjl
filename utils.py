
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


def extract_data_unit(data):    # 提取数据单元
    # 获取数据单元长度
    print("数据长度： ", len(data))
    data_unit_length = data[22] * 256 + data[23]
    print("数据单元长度： ", data_unit_length)

    # 提取数据单元
    end_position = 24 + data_unit_length
    data_unit = data[24:end_position]
    print("数据单元：")
    print_0x(data_unit)
    return data_unit, data_unit_length


def print_0x(data, show_result=True, hex2dec=False):       # 转码显示
    output = ""
    if hex2dec:
        for each in data:
            # print(each)
            output = output + "{:0>2x}".format(each) + " "
    else:
        for idx, each in enumerate(data):
            # print(each)
            output += str(idx) + ":" + "{:0>2d}".format(each) + " "
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