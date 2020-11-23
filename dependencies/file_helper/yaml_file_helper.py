#! /usr/bin/env python3
# coding: utf-8

from yaml import load, dump, FullLoader

'''
dependencies: PyYAML
'''


class YamlFileHelper(object):
    '''读取yaml文件中指定的章节'''

    def __init__(self, file_name: str = None) -> None:
        self.file_name = file_name
        self.file_content = self._read()

    def _read(self):
        with open(self.file_name, encoding='utf-8') as f:
            return load(f, Loader=FullLoader)

    def __str__(self):
        return dump(self.file_content)

    def get_data(self, top_section: str, second_section: str = None) -> str:
        '''通过指定的章节获取其中内容'''
        data = self.file_content.get(top_section)
        if second_section and data:
            data = data.get(second_section)
        return data


if __name__ == '__main__':
    yaml_helper = YamlFileHelper('./query_config.yaml')
    data = yaml_helper.get_data('givr', 'call_flow')
    print(data)
