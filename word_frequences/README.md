## 文件分析

此项目旨在提供一种方法计算固定长度的单词短语在日志文件中出现的频率

### 依赖组件:
+ Python >= 3.6
+ Other python dependencies: `pip install -r requirements.txt`

### 使用方法:
可以通过如下的命令获取到具体的参数信息
```
python3 .\word_frequences.py -h
usage: word_frequences.py [-h] [-i] [-l MATCH_LENGTH] [-t DISPLAY_NUM] [-r REGULAR_EXPRESSION] [-o OUTPUT_FILE]
                        [-f FILE_LIST [FILE_LIST ...]] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -i, --ignore_number   数学替换成*
  -l MATCH_LENGTH, --length MATCH_LENGTH
                        日志文件中查询的单词长度
  -t DISPLAY_NUM, --top DISPLAY_NUM
                        显示多少个结果，出现频率从高到低
  -r REGULAR_EXPRESSION, --reg REGULAR_EXPRESSION
                        需要分析文件的正则表达式，支持压缩文件包中的文件, 默认值是所有文件
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        结果输出文件，默认输出到屏幕
  -f FILE_LIST [FILE_LIST ...], --file FILE_LIST [FILE_LIST ...]
                        需要分析的文件列表或者目录
  -v, --version         show program's version number and exit
```