import re
from bs4 import BeautifulSoup


class AtCoderParser:
    def __init__(self):
        pass

    def parse(self, url, page):
        content = {'url': url}
        page = BeautifulSoup(page, 'lxml')
        content['contest_name'] = page.find('a', attrs={'class': 'contest-title'}).text
        content['file_name'] = url.split('/')[-1].lower()
        a = [_.get_text('\n') for _ in page.findAll('pre', attrs={'id': re.compile(r'pre-sample.*')})]
        a = [_.strip() for _ in a]
        a = a[:len(a) // 2]
        a = [[a[_], a[_ + 1]] for _ in range(0, len(a), 2)]
        for i in range(len(a)):
            content['sample_in%i' % i], content['sample_out%i' % i] = a[i][0], a[i][1]
        return content

    def match(self, url):
        return re.fullmatch(r'https://atcoder.jp/contests/.*/tasks/.*', url) is not None
