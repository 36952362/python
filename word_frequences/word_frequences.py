#!/usr/bin/env python3
# coding:utf-8

import os
import sys
import re
import tarfile
import argparse

DATA_MAX_BUFF = 1024 * 10
CODING_TYPE = 'UTF-8'
TOP_FREQUENCE_NUM = 100000
REDUECE_COUNT = 0
DISPLAY_NUM = 100
DEFAULT_SUB_WORDS_LEN = 4
RE_PATTERN = None
DIGIT_RE_PATTEN = re.compile(r'\d+')
OUTPUT_FILE = ''
DATA_BUFF = ''
IGNORE_NUM = False
TOTAL_LINES = 0
TOTAL_SIZE = 0
FILE_LIST = ''


def read_part(file_path, size=DATA_MAX_BUFF, encoding=CODING_TYPE):
    '分段获取文件内容'
    if tarfile.is_tarfile(file_path):
        return read_tar_gz_file_part(file_path, size, encoding)
    return read_normal_file_part(file_path, size, encoding)


def read_tar_gz_file_part(file_path, size=DATA_MAX_BUFF, encoding=CODING_TYPE):
    tar = tarfile.open(file_path, 'r:gz')
    total_count = len(tar.getmembers())
    tmp_count = 0
    for member in tar.getmembers():
        tmp_count += 1
        if not RE_PATTERN.match(member.name):
            print('   ({0}/{1}) {2} 不符合正则表达，忽略'.format(tmp_count, total_count, member.name))
            continue
        print('   ({0}/{1}) {2} 正在处理...'.format(tmp_count, total_count, member.name))
        f = tar.extractfile(member)
        if not None:
            while True:
                part = f.read(size)
                if part:
                    try:
                        yield part.decode(CODING_TYPE)
                    except Exception:
                        pass
                else:
                    break
    return None


def read_normal_file_part(file_path, size=DATA_MAX_BUFF, encoding=CODING_TYPE):
    with open(file_path, encoding=encoding) as f:
        while True:
            part = f.read(size)
            if part:
                yield part
            else:
                return None


def misra_gries(sub_words, sub_words_dict):
    if sub_words in sub_words_dict:
        sub_words_dict[sub_words] += 1
    else:
        if len(sub_words_dict) < TOP_FREQUENCE_NUM:
            sub_words_dict[sub_words] = 1
        else:
            for eachItem in list(sub_words_dict):
                sub_words_dict[eachItem] -= 1
                if sub_words_dict[eachItem] == 0:
                    sub_words_dict.pop(eachItem)
            global REDUECE_COUNT
            REDUECE_COUNT += 1


def analysis_file(file_name, sub_words_dict):
    global DATA_BUFF
    global TOTAL_LINES
    global TOTAL_SIZE
    for part in read_part(file_name):
        TOTAL_SIZE += len(part)
        DATA_BUFF = DATA_BUFF + part
        line_list = DATA_BUFF.split('\n')
        DATA_BUFF = line_list[-1]
        for line in line_list[:-1]:
            TOTAL_LINES += 1
            if IGNORE_NUM:
                line = DIGIT_RE_PATTEN.sub('*', line)
            words = line.split()
            while len(words) >= DEFAULT_SUB_WORDS_LEN:
                sub_words = ' '.join(words[:DEFAULT_SUB_WORDS_LEN])
                words = words[1:]
                misra_gries(sub_words, sub_words_dict)

    if len(DATA_BUFF) > 0:
        words = DATA_BUFF.split()
        while len(words) >= DEFAULT_SUB_WORDS_LEN:
            sub_words = ' '.join(words[:DEFAULT_SUB_WORDS_LEN])
            words = words[1:]
            misra_gries(sub_words, sub_words_dict)


def get_command_params():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ignore_number', dest='ignore_number', action='store_true', default=False, help='数学替换成*')
    parser.add_argument('-l', '--length', dest='match_length', action='store', default=4, type=int, help='日志文件中查询的单词长度')
    parser.add_argument('-t', '--top', dest='display_num', action='store', default=100, type=int, help='显示多少个结果，出现频率从高到低')
    parser.add_argument('-r', '--reg', dest='regular_expression', action='store', default='', help='需要分析文件的正则表达式，支持压缩文件包中的文件, 默认值是所有文件')
    parser.add_argument('-o', '--output', dest='output_file', action='store', default='', help='结果输出文件，默认输出到屏幕')
    parser.add_argument('-f', '--file', dest='file_list', action='store', nargs='+', help='需要分析的文件列表或者目录')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    input_params = parser.parse_args()

    global IGNORE_NUM
    IGNORE_NUM = input_params.ignore_number

    if not check_regular_expression(input_params.regular_expression):
        sys.exit(1)

    if not check_display_num(input_params.display_num):
        sys.exit(2)

    if not check_match_length(input_params.match_length):
        sys.exit(3)

    if not check_output_file(input_params.output_file):
        sys.exit(4)

    print(input_params.file_list)
    valid_file_list = get_input_file_list(input_params.file_list)
    if not valid_file_list:
        sys.exit(5)

    global FILE_LIST
    FILE_LIST = valid_file_list


def get_input_file_list(file_list: str) -> list:
    '''需要分析的文件列表或者目录'''
    if not file_list:
        print('请输入要分析的文件或目录')
        return None

    valid_file_list = []
    for file in file_list:
        if not os.path.exists(file):
            print('{0} 不存在，忽略'.format(file))
            continue
        if os.path.isfile(file) and not tarfile.is_tarfile(file) and not RE_PATTERN.match(file):
            print('{0} 不符合正则表达式, 忽略'.format(file))
            continue

        valid_file_list.append(file)
    if len(valid_file_list) == 0:
        print('输入的文件或目录不存在')
        return None

    return valid_file_list


def check_output_file(output_file: str) -> bool:
    '''检查输出目录'''
    global OUTPUT_FILE
    if len(output_file) > 0 and not os.path.exists(output_file):
        dir_name = os.path.dirname(os.path.abspath(output_file))
        if not os.path.exists(dir_name):
            print('结果输出文件目录不存在', dir_name)
            return False
    OUTPUT_FILE = output_file
    return True


def check_regular_expression(regular_expression: str) -> bool:
    '''获取文件名的正则表达式'''
    if len(regular_expression) == 0:
        regular_expression = r'.*'
    global RE_PATTERN
    try:
        RE_PATTERN = re.compile(regular_expression)
    except Exception as ex:
        print('正则表达式不正确', str(ex))
        return False
    return True


def check_display_num(display_num: int) -> bool:
    '''显示多少个结果，出现频率从高到低'''
    if display_num < 0:
        return False

    global DISPLAY_NUM
    DISPLAY_NUM = display_num
    return True


def check_match_length(match_length: int) -> bool:
    '''日志文件中查询的单词长度'''
    if match_length < 0:
        return False

    global DEFAULT_SUB_WORDS_LEN
    DEFAULT_SUB_WORDS_LEN = match_length

    return True


def get_file_path():
    '''获取需要分析的文件或目录'''
    file_path = None
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        try:
            file_path = input('需要分析的文件或目录:')
        except Exception:
            return None
    if os.path.exists(file_path):
        return file_path
    else:
        return None


def get_all_file_list(file_list):
    '获取需要分析的文件列表'
    all_file_list = []
    for file in file_list:
        if os.path.isfile(file):
            all_file_list.append(file)
        if os.path.isdir(file):
            all_file_list.extend(get_all_file_list_from_dir(file))

    return all_file_list


def get_all_file_list_from_dir(root_dir):
    file_list = []
    for root, dirs, files in os.walk(root_dir):    # 分别代表根目录、文件夹、文件
        for file in files:                         # 遍历文件
            file_path = os.path.join(root, file)   # 获取文件绝对路径
            file_list.append(file_path)            # 将文件路径添加进列表
        for dir in dirs:                           # 遍历目录下的子目录
            dir_path = os.path.join(root, dir)     # 获取子目录路径
            file_list.extend(get_all_file_list_from_dir(dir_path))  # 递归调用
    return file_list


def analysis_files(file_list):
    sub_words_dict = dict()
    all_file_list = get_all_file_list(file_list)
    totol_count = len(all_file_list)
    tmp_count = 0
    for file in all_file_list:
        tmp_count += 1
        base_name = os.path.basename(file)
        if not tarfile.is_tarfile(file) and not RE_PATTERN.match(base_name):
            print('[{0}/{1}] {2} 不符合正则表达式,忽略此文件'.format(tmp_count, totol_count, file))
            continue
        print('[{0}/{1}] {2} 分析中...'.format(tmp_count, totol_count, file))
        analysis_file(file, sub_words_dict)
    sorted_by_value = sorted(sub_words_dict.items(), key=lambda item: item[1], reverse=True)
    return sorted_by_value


def display_result(result):
    if len(result) == 0:
        print('分析出错，退出')
        return

    global OUTPUT_FILE
    global TOTAL_LINES
    global TOTAL_SIZE
    if len(OUTPUT_FILE) > 0:
        if os.path.isdir(OUTPUT_FILE):
            OUTPUT_FILE = os.path.join(os.path.abspath(OUTPUT_FILE), 'result.log')
        file = open(OUTPUT_FILE, 'w', encoding='utf-8')

    total_line_str = "总行数:{0}".format(TOTAL_LINES)
    total_size_str = "总字节数:{0}".format(TOTAL_SIZE)

    print(total_line_str)
    print(total_size_str)
    if len(OUTPUT_FILE) > 0:
        file.write(total_line_str + '\n')
        file.write(total_size_str + '\n')

    count = 1
    for item in result[:DISPLAY_NUM]:
        item_frequency = item[1] + REDUECE_COUNT
        line_ratio = round(item_frequency / TOTAL_LINES * 100, 6)
        size_ratio = round((len(item[0])*item_frequency) / TOTAL_SIZE * 100, 6)
        line = '{0}.出现次数:{1}, 行占比:{2}%, 字节占比:{3}%, 查询语句:{4}'.format(count, item_frequency, line_ratio, size_ratio, item[0])
        count += 1
        print(line)
        if len(OUTPUT_FILE) > 0:
            file.write(line + '\n')

    if len(OUTPUT_FILE) > 0:
        file.close()
        print('查询结果保存在{0}'.format(OUTPUT_FILE))


def get_sub_words_len():
    if len(sys.argv) > 2:
        return int(sys.argv[2])
    return DEFAULT_SUB_WORDS_LEN


def main():
    file_list = get_command_params()
    result = analysis_files(file_list)
    display_result(result)


if __name__ == '__main__':
    main()
