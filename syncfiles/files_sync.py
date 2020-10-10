#!/usr/bin/env python3
#coding: utf-8

import os, subprocess
import argparse
import pexpect
from paramiko import SSHClient
from scp import SCPClient

LOCAL_Project_PATH_BASE = '.'
REMOTE_IP = '10.224.85.89'
REMOTE_USER_NAME = 'root'
REMOTE_USER_PASSWORD = 'webexlinux'
REMOTE_WORKSPACE_PATH_BASE = '/spare/workspace'

IGNORE_FILE_LIST = [
]

def get_change_file_list(check_dir):
    local_project_path = LOCAL_Project_PATH_BASE + os.sep + check_dir
    stdoutput = subprocess.check_output('cd %s && git status -suno' %local_project_path, shell=True)
    decoded_data = stdoutput.decode('UTF-8')
    file_list = []
    print('Change file list:')
    for file in decoded_data.split('\n'):
        file_name = file.strip().split()
        if len(file_name) > 1:
            if file_name[0] == 'D' or file_name[0] == 'R' or file_name[1] in IGNORE_FILE_LIST:
                continue
            file_list.append(file_name[1])
            print('  ', file_name[1])
    print('')
    return file_list


#this method, it needs to generate id_rsa.pub and copy to remote host, make this server as trusted
#It can used both on windows and linux
def scp_copy_files(file_list, check_dir):
    local_project_path =  LOCAL_Project_PATH_BASE + os.sep + check_dir
    remote_project_path = REMOTE_WORKSPACE_PATH_BASE + '/' + check_dir
    for file in file_list:
        print('handle ', file)
        local_file_path = local_project_path + os.sep + file
        remote_file_path = REMOTE_USER_NAME + '@' + REMOTE_IP + ":" + remote_project_path + '/' + os.path.dirname(file) + "/"
        p = subprocess.Popen('scp %s %s' %(local_file_path, remote_file_path), shell=True)
        p.wait()

#this method uses pscp.exe to copy file, but it uses plaintext password in command
#Only used in windows
def pscp_copy_files(file_list, check_dir):
    local_project_path =  LOCAL_Project_PATH_BASE + os.sep + check_dir
    remote_project_path = REMOTE_WORKSPACE_PATH_BASE + '/' + check_dir
    for file in file_list:
        print('handle ', file)
        local_file_path = local_project_path + os.sep + file
        remote_file_path = REMOTE_USER_NAME + '@' + REMOTE_IP + ":" + remote_project_path + '/' + os.path.dirname(file) + "/"
        subprocess.check_output(['powershell', '-command', './pscp.exe', '-pw ' + REMOTE_USER_PASSWORD, local_file_path,  remote_file_path])

#this method uses paramiko and scp to copy files and secured
#It needs add remote server address into ~/.ssh/known_hosts file firstly
#It can used both on windows and linux
def ssh_scp_files(file_list, check_dir):
    #ssh_host, ssh_user, ssh_password, ssh_port, source_volume, destination_volume):
    local_project_path =  LOCAL_Project_PATH_BASE + os.sep + check_dir
    remote_project_path = REMOTE_WORKSPACE_PATH_BASE + '/' + check_dir
    ssh = SSHClient()
    #ssh.load_system_host_keys()
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect(REMOTE_IP, username=REMOTE_USER_NAME, password=REMOTE_USER_PASSWORD, look_for_keys=False)
    with SCPClient(ssh.get_transport()) as scp:
        local_project_path =  LOCAL_Project_PATH_BASE + os.sep + check_dir
        remote_project_path = REMOTE_WORKSPACE_PATH_BASE + '/' + check_dir
        for file in file_list:
            local_file_path = local_project_path + os.sep + file
            remote_file_path = remote_project_path + '/' + os.path.dirname(file) + "/"
            print('handle ', local_file_path)
            scp.put(local_file_path, recursive=True, remote_path=remote_file_path)

#this method uses pexpect to copy files
#It can only running on linux
def pexpect_copy_files(file_list, check_dir, timeout=30): 
    local_project_path =  LOCAL_Project_PATH_BASE + os.sep + check_dir
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
    parser.add_argument('-d', '--dir', dest='dir', action='store', default='webex-telephony-tahoe', help='check directory')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true', help='quiet, dont show interaction')
    return parser.parse_args()

def get_confirm():
    result = input('Continue[Y/N]:')
    if result.lower() == 'y':
        return True
    else:
        return False

def main(): 
    input_args = get_input_arguments()
    check_dir = input_args.dir
    file_list = get_change_file_list(check_dir)
    if len(file_list) == 0:
        print('No file change,exit')
        return

    if(input_args.quiet or get_confirm()):
        #there are 4 methods for differenct scenario
        ssh_scp_files(file_list, check_dir)
        #scp_copy_files(file_list, check_dir)
        #pscp_copy_files(file_list, check_dir)
        #pexpect_copy_files(file_list, check_dir)
        
    else:
        print('Abort')


if __name__ == '__main__':
    main()