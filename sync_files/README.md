## 同步文件

此项目旨在提供一种方法解决开发和编译在不同的机器上。通过`git status`命令获取到在开发机器上的改动文件列表，然后通过系统的`scp`命令把改动的文件列表拷贝到编辑机器所在项目对应的文件夹中。从而提高项目的开发效率。

### 依赖组件:
+ Python >= 3.6
+ Other python dependencies: `pip install -r requirements.txt`

### 使用方法:
根据不同的平台和使用场景，提供了4种使用方式:

#### `ssh_scp_files`
+ 这种方式先使用`paramiko`进行`ssh`链接，然后使用scp同步文件列表
+ 好处是在同步的过程中不会暴露用户名和密码，同时在windows和linux平台下都可以使用
+ 前提条件是需要把远端服务器的地址存储到本地的~/.ssh/known_hosts 文件中， 也就是第一次使用之前要成功手工执行一下scp的命令并存储远端服务器的地址

#### `scp_copy_files`
+ 这种方式使用subprocess的方式同步文件列表
+ 好处是在同步的过程中不会暴露用户名和密码，同时在windows和linux平台下都可以使用
+ 前提条件是需要把在本地服务器生成id_rsa.pub并拷贝到远端服务器

#### `pscp_copy_files`
+ 这种方式借助于pscp.exe第三方软件同步文件列表，只能在windows平台使用
+ 在同步的过程中能看到明文用户名和密码

#### `pexpect_copy_files`
+ 这种方式使用`pexpect`同步文件列表, 只能在linux平台使用
+ 在同步的过程中能看到明文用户名和密码

### 举例
```
PS C:\Users\jupiter\Documents\workspace> pwd                                                                           
Path
----
C:\Users\jupiter\Documents\workspace

PS C:\Users\jupiter\Documents\workspace> python3 .\files_sync.py -d python 
改动文件列表:
   README.md
   syncfiles/files_sync.py

确定[Y/N]: y
正在处理  .\python\README.md
正在处理  .\python\syncfiles/files_sync.py
PS C:\Users\jupiter\Documents\workspace>
```