#!/usr/bin/env python3
# coding: utf-8

from datetime import datetime, timedelta
from pytz import timezone
import time
import qrcode
import zxing

'''
dependences: pytz, qrcode, zxing
'''


def unix_time(dt):
    # 转换成时间数组
    timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    # 转换成时间戳
    timestamp = int(time.mktime(timeArray))*1000
    return timestamp


def local_time(timeNum):
    timeStamp = float(timeNum / 1000)
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


def get_time_as_string(dt=None, fmt_str='%Y-%m-%dT%H:%M:%S', day_delta=None, tz=None):
    if not dt:
        if not tz:
            tz = timezone('UTC')
        dt = datetime.now(tz)
    if not day_delta:
        delta = timedelta(days=day_delta)
        dt = dt + delta
    return dt.strftime(fmt_str)


def get_begin_end_time_by_duration(duration, guard_time=None, tz=None, forward=True):
    if not tz:
        tz = timezone('UTC')

    if not guard_time:
        guard_time = datetime.now(tz)

    delta = None

    if 'd' in duration:
        duration = duration.replace('d', '')
        delta = timedelta(days=int(duration))
    elif 'h' in duration:
        duration = duration.replace('h', '')
        delta = timedelta(hours=int(duration))
    elif 'm' in duration:
        duration = duration.replace('m', '')
        delta = timedelta(minutes=int(duration))
    elif 's' in duration:
        duration = duration.replace('s', '')
        delta = timedelta(seconds=int(duration))

    if forward:
        begin_time = guard_time
        end_time = begin_time + delta
    else:
        end_time = guard_time
        begin_time = end_time - delta
    return begin_time, end_time


def generate_qrcode(url: str):
    '''通过一个URL 生成一个二维码的图片'''
    image = qrcode.make(data=url)
    return image


def decode_qrcode_image(image_file):
    '''通过一个二维码图片提取对应的URL'''
    reader = zxing.BarCodeReader()
    barcode = reader.decode(image_file)
    return barcode.parsed


if __name__ == "__main__":
    print(unix_time("2020-02-24 01:01:01"))
    img = generate_qrcode("https://www.baidu.com")
    # img.show()
    img.save("baidu.jpg")
    url = decode_qrcode_image('baidu.jpg')
    print(url)
