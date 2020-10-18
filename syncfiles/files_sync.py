#!/usr/bin/env python3
# coding: utf-8

import os
import subprocess
import argparse
import pexpect
from paramiko import SSHClient
from scp import SCPClient

LOCAL_Project_PATH_BASE = '.'
REMOTE_IP = '127.0.0.2'
REMOTE_USER_NAME = 'root'
REMOTE_USER_PASSWORD = 'pass'
REMOTE_WORKSPACE_PATH_BASE = '/spare/workspace'

IGNORE_FILE_LIST = [
]


# 通过git status 命令获取项目中改动的文件列表
def get_changed_file_list(check_dir):
    local_project_path = LOCAL_Project_PATH_BASE + os.sep + check_dir
    stdoutput = subprocess.check_output('cd %s && git status -suno' % local_project_path, shell=True)
    decoded_data = stdoutput.decode('UTF-8')
    changed_file_list = []
    print('改动文件列表:')
    for file in decoded_data.split('\n'):
        file_name = file.strip().split()
        if len(file_name) > 1:
            if file_name[0] == 'D' or file_name[0] == 'R' or file_name[1] in IGNORE_FILE_LIST:
                continue
            changed_file_list.append(file_name[1])
            print('  ', file_name[1])
    print('')
    return changed_file_list


# 这种方式使用subprocess的方式同步文件列表
# 好处是在同步的过程中不会暴露用户名和密码，同时在windows和linux平台下都可以使用
# 前提条件是需要把在本地服务器生成id_rsa.pub并拷贝到远端服务器
def scp_copy_files(file_list, check_dir):
    local_project_path = LOCAL_Project_PATH_BASE + os.sep + check_dir
    remote_project_path = REMOTE_WORKSPACE_PATH_BASE + '/' + check_dir
    for file in file_list:
        print('正在处理 ', file)
        local_file_path = local_project_path + os.sep + file
        remote_file_path = REMOTE_USER_NAME + '@' + REMOTE_IP + ":" + remote_project_path + '/' + os.path.dirname(file) + "/"
        p = subprocess.Popen('scp %s %s' % (local_file_path, remote_file_path), shell=True)
        p.wait()


# 这种方式借助于pscp.exe第三方软件同步文件列表，只能在windows平台使用
# 在同步的过程中能看到明文用户名和密码
def pscp_copy_files(file_list, check_dir):
    local_project_path = LOCAL_Project_PATH_BASE + os.sep + check_dir
    remote_project_path = REMOTE_WORKSPACE_PATH_BASE + '/' + check_dir
    for file in file_list:
        print('handle ', file)
        local_file_path = local_project_path + os.sep + file
        remote_file_path = REMOTE_USER_NAME + '@' + REMOTE_IP + ":" + remote_project_path + '/' + os.path.dirname(file) + "/"
        subprocess.check_output(['powershell', '-command', './pscp.exe', '-pw ' + REMOTE_USER_PASSWORD, local_file_path,  remote_file_path])


# 这种方式先使用paramiko进行ssh链接，然后使用scp同步文件列表
# 好处是在同步的过程中不会暴露用户名和密码，同时在windows和linux平台下都可以使用
# 前提条件是需要把远端服务器的地址存储到本地的~/.ssh/known_hosts 文件中， 也就是第一次使用之前要成功手工执行一下scp的命令并存储远端服务器的地址
def ssh_scp_files(file_list, check_dir):
    # ssh_host, ssh_user, ssh_password, ssh_port, source_volume, destination_volume):
    local_project_path = LOCAL_Project_PATH_BASE + os.sep + check_dir
    remote_project_path = REMOTE_WORKSPACE_PATH_BASE + '/' + check_dir
    ssh = SSHClient()
    # ssh.load_system_host_keys()
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect(REMOTE_IP, username=REMOTE_USER_NAME, password=REMOTE_USER_PASSWORD, look_for_keys=False)
    with SCPClient(ssh.get_transport()) as scp:
        local_project_path = LOCAL_Project_PATH_BASE + os.sep + check_dir
        remote_project_path = REMOTE_WORKSPACE_PATH_BASE + '/' + check_dir
        for file in file_list:
            local_file_path = local_project_path + os.sep + file
            remote_file_path = remote_project_path + '/' + os.path.dirname(file) + "/"
            print('正在处理 ', local_file_path)
            scp.put(local_file_path, recursive=True, remote_path=remote_file_path)


# 这种方式使用pexpect同步文件列表, 只能在linux平台使用
# 在同步的过程中能看到明文用户名和密码
def pexpect_copy_files(file_list, check_dir, timeout=30):
    local_project_path = LOCAL_Project_PATH_BASE + os.sep + check_dir
    remote_project_path = REMOTE_WORKSPACE_PATH_BASE + '/' + check_dir
    for file in file_list:
        print('handle ', file)
        local_file_path = local_project_path + os.sep + file
        remote_file_path = REMOTE_USER_NAME + '@' + REMOTE_IP + ":" + remote_project_path + '/' + os.path.dirname(file) + "/"
        scp_cmd = 'scp %s %s' % (local_file_path, remote_file_path)
        child = pexpect.spawn(scp_cmd, timeout=timeout)
        child.expect(['password: '])
        child.sendline(REMOTE_USER_PASSWORD)
        child.expect(pexpect.EOF)
        child.close()


def get_input_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', dest='dir', action='store', default='python', help='check directory')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true', help='quiet, dont show interaction')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    return parser.parse_args()


def get_confirm():
    result = input('确定[Y/N]:')
    if result.lower() == 'y':
        return True
    else:
        return False


def main():
    # 获取检查项目目录和输入参数
    input_args = get_input_arguments()
    check_dir = input_args.dir

    # 获取项目中改动的文件列表
    changed_file_list = get_changed_file_list(check_dir)
    if len(changed_file_list) == 0:
        print('没有文件改动，退出')
        return

    if(input_args.quiet or get_confirm()):
        # 根据不同的操作系统平台和应用场景，提供四种方式同步文件
        ssh_scp_files(changed_file_list, check_dir)
        # scp_copy_files(changed_file_list, check_dir)
        # pscp_copy_files(changed_file_list, check_dir)
        # pexpect_copy_files(changed_file_list, check_dir)

    else:
        print('Abort')


if __name__ == '__main__':
    main()
