import re


class PEParser:
    def parse(self, url, page):
        content = {'url': url}
        content['contest_name'] = 'Project Euler'
        content['file_name'] = content['problem_name'] = url.split('=')[-1]
        content['sample_in0'] = ''
        return content

    def match(self, url):
        return re.fullmatch(r'https://projecteuler.net/problem=\d*', url) is not None
