#! /usr/bin/env python3
# coding: utf-8

from yaml import load, dump, FullLoader
import logging


class YamlFileHelper(object):
    def __init__(self, file_name=None):
        self.file_name = file_name
        self.file_content = self._read()
        logging.info('file_name:{0}'.format(self.file_name))

    def _read(self):
        with open(self.file_name, encoding='utf-8') as f:
            return load(f, Loader=FullLoader)

    def __str__(self):
        return dump(self.file_content)

    def get_data(self, top_section, second_section=None):
        data = self.file_content.get(top_section)

        if second_section and data:
            data = data.get(second_section)
        return data


if __name__ == '__main__':
    logging.basicConfig(filename='../logs/yamlfilehelper.log', format='[%(asctime)s]%(levelname)s:%(message)s', filemode='w', level=logging.DEBUG)
    yaml_helper = YamlFileHelper('../config/query_config.yaml')
    # data = yaml_helper.get_data('givr', 'call_flow')
    yaml_helper.get_keys()
    # logging.info(data)
    # print(data)
