#!/usr/bin/env python
# -*- coding:utf-8 -*-


def process_message(data):
    if data[0] != 0x23 or data[1] != 0x23:
        return False
    if data[2] == 0x23:
        pass


def main():
    with open("binlog.txt", "rb+") as binfile:
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


if __name__ == '__main__':
    main()
