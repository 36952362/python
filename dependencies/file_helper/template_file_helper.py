#! /usr/bin/env python3
# coding: utf-8
'''
dependences: jinja2
'''

from jinja2 import Template
import logging


class TemplateFileHelper(object):
    '''该函数通过一个j2模板文件和传入的参数生成最终的j2文件'''

    def __init__(self, file_name: str) -> None:
        self.logger = logging.getLogger(__name__)
        self.file_name = file_name
        with open(self.file_name, "r") as src_file:
            self.template = Template(src_file.read())

    def output(self, **kwargs: dict):
        '''根据输入的字典参数产生最终的j2w文件'''
        output = self.template.render(kwargs)
        return output


if __name__ == '__main__':
    params = {
        'queryString': 'querystring',
        'beginTime': 'beginTime',
        'endTime': 'endTime'
    }
    template_helper = TemplateFileHelper('./simple_query.j2')
    output = template_helper.output(**params)
    print(output)
