## 导出安卓微信消息记录
此程序旨在导出安卓手机上的微信消息记录，并进行合适的格式化以方便阅读和查阅。
运行此程序之前需要通过一些步骤把手机上的微信消息记录导出才能进行后续的操作。

### 依赖组件:
+ Python >= 3.6
+ Other python dependencies: `pip install -r requirements.txt`

### 使用方法:

### 一. 从手机上导出微信消息记录
由于微信的消息记录在手机上存储在系统目录中，正常情况下如果不对手机进行`root`操作是不能获取的相关数据的。

+ 一种方式是通过技术手段对手机进行`root`来获取微信数据，但是不同品牌的手机对`root`操作有各种各样的限制，同时被`root`过的手机在使用的过程中存储安全风险。

+ 另一种方式是借助于微信本身自带的消息转储功能，首先把真实手机中的微信消息转储到电脑中，然后再把电脑中的微信消息转储到一个手机模拟器中。这样手机模拟器进行`root`操作，就可以间接的方式获取到微信消息记录。

本文中介绍如何采用第二种方式获取到微信的消息记录：
+ 备份微信记录
  + 在电脑上下载微信软件并登陆
  + 把手机端聊天记录备份到电脑端微信
  + 在电脑上下载安卓手机模拟器(比如:夜神模拟器)
  + 启动模拟器，在模拟器中下载微信软件并登陆
  + 把电脑端聊天记录恢复到安卓虚拟器里的微信

+ 获取微信数据库
  + 打开模拟器中的文件管理器并跳转到`/data/data/com.tencent.mm/MicroMsg`目录，在操作过程中提示提升权限时选择"是"
  + 在此目录中找到由32位字母和数据组成的文件夹，此处可能有多个。可以通过文件夹的最后修改时间来确定需要获取的到底是哪个目录
  + 进入32位字母和数据组成的文件夹，把此文件夹中的`EnMicroMsg.db`拷贝到`/mnt/shared/other`目录
  + 从电脑端和模拟器共享目录中就可以获取到微信数据库`EnMicroMsg.db`

+ 获取数据库密钥
  + EnMicroMsg.db是加密文件。 加密方式是：首先需要获得手机的IMEI码（一般15位）和微信的uin码（9位），然后将IMEI码和uin码顺序连接，然后用MD5算法加密，小写密文的前七位就是数据库的密码了
  + 手机IMEI码获取: 在手机拨号键盘上输入 *#06# 即可获得，有些手机可能有多个IMEI码，那可以每一个都试一下。在夜神模拟器的系统设置中也可以获取到对应的IMEI码
  + 微信uin码获取：在模拟器的`/data/data/com.tencent.mm/shared_prefs`目录：
    + `system_config_prefs.xml`文件中`default_uin`对应的值就是uin码(不需要关心是否是负数，当成完整字符串即可)
      ```
      <int name="default_uin" value="-1734087169" />
      ```
    + `com.tencent.mm_preferences.xml`文件中`last_login_uin`对应的值也是uin码(通常这个值跟`system_config_prefs.xml`中的值是一样的，如果不同可以2个都尝试一下)
      ```
      <string name="last_login_uin">-1734087169</string>
      ```
  + 拿到这两串数字之后，利用[MD5加密网站](https://www.sojson.com/encrypt_md5.html)加密，输入IMEI + uin （没有+号，俩串字符直接连起来），选取32位小写密文的前7个字符，这就是我们的数据库密钥了
+ 解密数据库
    借助于`sqlcipher.exe`并结合`IMEI`和`UIN`生成的MD5密码对加密的数据库`EnMircroMsg.db`进行解密。如果执行成功后，就会生成一个非加密的`decrepted.db`. 其中的`PRAGMA key`对应的值换成`IMEI`和`UIN`生成的MD5密码;如果在运行下面的命令出现错误时，建议先使用`sqlcipher_gui.exe`手工输入密码确认上传的MD5密码是否正确。
    ```
    sqlcipher EnMicroMsg.db
    PRAGMA key = "7ee2ac9";
    PRAGMA cipher_use_hmac = off;
    PRAGMA kdf_iter = 4000;
    ATTACH 'decrepted.db' AS decrepted KEY '';
    SELECT sqlcipher_export('decrepted');
    DETACH DATABASE decrepted;
    ```
+ 导出微信消息记录
  使用`dump-msg.py`脚本获取到数据库中信息，并按照用户名或者群名生成文本文件。这个脚本只能导出文件消息，不支持语音、视频、图片、链接和下载文件的导出。
  ```
  ./dump-msg.py decrypted.db <output-dir>
  ```
