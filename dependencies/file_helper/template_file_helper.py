#! /usr/bin/env python3
# coding: utf-8

from jinja2 import Template
import logging


class TemplateFileHelper(object):
    def __init__(self, file_name, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.file_name = file_name
        self.params = kwargs
        with open(self.file_name, "r") as src_file:
            self.template = Template(src_file.read())

    def output(self):
        output = self.template.render(self.params)
        return output


if __name__ == '__main__':
    params = {
        'queryString': 'querystring',
        'beginTime': 'beginTime',
        'endTime': 'endTime'
    }
    template_helper = TemplateFileHelper('../templates/simple_query.j2', **params)
    output = template_helper.output()
    print(output)
