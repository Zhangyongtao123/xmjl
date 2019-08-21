#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time, datetime


def hex_str(data):
    output = ""
    for each in data:
        output = output + "{:0>2x}".format(each) + " "
    return output


def cal_checksum(data):
    checksum = 0
    for each in data[0:len(data) - 1]:
        checksum = checksum ^ each
    return checksum


def check_error(data):
    checksum = 0
    for each in data[0:len(data)]:
        checksum = checksum ^ each
    return not checksum


def validate(data):
    if data[0] != 0x23 or data[1] != 0x23 or data[3] != 0xfe:
        print("validate message error")
        return False
    payload_size = int.from_bytes(data[22:24], byteorder='big')
    if (payload_size + 25) != len(data):
        return False
    return True


def gmt2timestamp(time_data):
    time_str = "%d %d %d %d %d %d" % (time_data[0], time_data[1], time_data[2], time_data[3], time_data[4], time_data[5])
    time_arrary = time.strptime(time_str, "%y %m %d %H %M %S")
    timestamp = int(time.mktime(time_arrary))
    return timestamp


def timestamp2gmt(timestamp):
    gmt_time = datetime.datetime.fromtimestamp(timestamp)
    time_str = gmt_time.strftime("%y %m %d %H %M %S")
    print("time_str: "+time_str)
    time_lst = time_str.split()
    byte_seq = b""
    for each in time_lst:
        byte_seq += int.to_bytes(int(each), 1, byteorder="big")
    return byte_seq
    #print("GMT+8 time in bytes: ", hex_str(byte_seq))


def get_cur_time():
    cur_time_str = datetime.datetime.now().strftime("%y %m %d %H %M %S")
    print("cur_time_str: " + cur_time_str)
    time_lst = cur_time_str.split()
    byte_seq = b""
    for each in time_lst:
        byte_seq += int.to_bytes(int(each), 1, byteorder="big")
    return byte_seq
    #print("GMT+8 time in bytes: ", hex_str(byte_seq))


def generate_response(data, flag):
    time_byte_seq = get_cur_time()
    new_msg = data[0:3] + int.to_bytes(flag, 1, byteorder="big") + data[4:24] + time_byte_seq + data[30:]
    checksum = cal_checksum(new_msg)
    res = new_msg[0:-1] + int.to_bytes(checksum, 1, byteorder="big")
    return res


def process_message(data):
    VIN = data[4:21].decode()
    print("VIN: ", VIN)
    if data[2] == 0x1:
        print("new timestamp: ", gmt2timestamp(data[24:30]))
        get_cur_time()
        #print(int(time.time()))
        pass
    elif data[2] == 0x2:
        pass
    elif data[2] == 0x3:
        pass
    elif data[2] == 0x4:
        pass
    else:
        # TODO: return an error response body
        pass


def main():
    with open("virtuallog.txt", "rb+") as binfile:
        data = binfile.read()
    checkres = 0
    output = ""
    for each in data:
        output = output + "{:0>2x}".format(each) + " "
        checkres = checkres ^ each
    size = len(data)
    checksum = 0
    for i in range(0, size - 1):
        checksum = checksum ^ data[i]
    print(output)
    print("checksum: " + "{:0>2x}".format(checksum))
    print("checkres: " + "{:0>2x}".format(checkres))
    process_message(data)

    res = generate_response(data, 0x1)
    print(hex_str(res))


if __name__ == '__main__':
    main()
