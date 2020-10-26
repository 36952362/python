#!/usr/bin/env python3
# coding:utf-8
'''
此程序旨在导出安卓手机上的微信消息记录，并进行合适的格式化以方便阅读和查阅。
运行此程序之前需要通过一些步骤把手机上的微信消息记录导出才能进行后续的操作。
具体操作请参阅README.md
'''
import sqlite3
import sys
import os
import argparse
from dependencies.misc.tools import local_time


def export_record_to_dic(record_list: list) -> dict:
    '''遍历所有记录并按照联系人或者群名输出到字典中'''
    talker_records_dict = dict()
    for i in range(0, len(record_list)):
        talker = record_list[i][2]
        tmp_record_list = talker_records_dict.get(talker)
        if not tmp_record_list:
            tmp_record_list = list()
            talker_records_dict[talker] = tmp_record_list
        tmp_record_list = talker_records_dict[talker]
        tmp_record_list.append(record_list[i])
    return talker_records_dict


def dump_record(talker_record_dict: dict) -> None:
    '''遍历所有的消息记录'''
    for talker in talker_record_dict:
        dump_talker_messages(talker, talker_record_dict[talker])


def dump_talker_messages(talker: str, record_list: list) -> None:
    '''导出每个联系人或者群名的消息记录'''
    formatted_records = list()
    for each_record in record_list:
        formatted_record = format_each_record(talker, each_record)
        formatted_records.append(formatted_record)
    dump_record_to_file(talker, formatted_records)


def dump_record_to_file(talker: str, formatted_records: list) -> None:
    '''输出记录到文件中'''
    fileName = os.path.join(output_dir, talker + '的聊天记录.txt')
    with open(fileName, 'wb') as f:
        for eachMessage in formatted_records:
            f.write((eachMessage + '\n').encode('utf-8'))


def format_personal_record(talker: str, each_record: str) -> str:
    '''格式化1对1聊天记录'''
    if need_dump(each_record[4]):
        final_record = local_time(each_record[1])
        if each_record[0] == 0:
            final_record = final_record + ' ' + talker + ':'
        else:
            final_record = final_record + ' 我：'
        final_record = final_record + each_record[4]
        return final_record


def format_group_record(each_record: str) -> str:
    '''格式化群聊'''
    if need_dump(each_record[4]):
        final_record = local_time(each_record[1])
        if each_record[0] == 1:
            final_record = final_record + ' 我:'
        final_record = final_record + ' ' + each_record[4]
        return final_record


def format_each_record(talker: str, each_record: str) -> str:
    '''格式化每条记录'''
    if is_group(talker):
        return format_group_record(each_record)
    else:
        return format_personal_record(talker, each_record)


def is_group(talker: str) -> bool:
    '''判断记录是否是群聊'''
    if 'chatroom' in talker:
        return True
    return False


def need_dump(each_record: str) -> bool:
    '''过滤掉无效的记录，只保留文本内容'''
    if '<msg>' in each_record:
        return False
    if 'wxid_' in each_record:
        return False
    return True


def get_records(db_file: str) -> list:
    '''获取数据库中的记录'''
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    # sql = "select isSend,createTime,talker,type,content from message where talker = 'wxid_'
    # and createTime > "+str(b)+" and createTime < "+str(e)+" and type = '1'order by createTime"
    sql = "select isSend,createTime,talker,type,content from message order by createTime"
    cursor = c.execute(sql)
    records = cursor.fetchall()
    conn.close()
    return records


def get_command_params():
    '''获取命令行参数'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--db', action='store', dest='db_file', default='decrypted.db', help='需要导出的非加密数据库')
    parser.add_argument('-o', '--output', action='store', dest='output_dir', help='导出消息目录')
    return parser.parse_args()


if __name__ == "__main__":
    args = get_command_params()
    db_file = args.db_file
    output_dir = args.output_dir
    try:
        os.mkdir(output_dir)
    except Exception:
        pass
    if not os.path.isdir(output_dir):
        sys.exit("创建目录{}失败".format(output_dir))

    record_list = get_records(db_file)
    talker_record_dict = export_record_to_dic(record_list)
    dump_record(talker_record_dict)
