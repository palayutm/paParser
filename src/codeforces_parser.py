import re
from bs4 import BeautifulSoup


class CodeforcesParser:
    def __init__(self):
        pass

    def parse(self, url, page):
        content = {'url': url}
        page = BeautifulSoup(page, 'lxml')
        if url.find('problemset') >= 0:
            content['contest_name'] = 'Codeforces Practice'
            content['file_name'] = ''.join(url.split('/')[-2:])
        else:
            content['contest_name'] = page.find('table', attrs={'class': 'rtable'}).find('tr').find('a').text
            content['file_name'] = url.split('/')[-1].lower()
        content['problem_name'] = page.find('div', attrs={'class': 'title'}).text
        a = [_.get_text('\n') for _ in page.findAll('div', attrs={'class': 'sample-test'})[0].findAll('pre')]
        a = [_.strip() for _ in a]
        a = [[a[_], a[_ + 1]] for _ in range(0, len(a), 2)]
        for i in range(len(a)):
            content['sample_in%i' % i], content['sample_out%i' % i] = a[i][0], a[i][1]
        return content

    def match(self, url):
        return re.fullmatch(r'https?://codeforces\.com/(contest|problemset|gym)/(\d*/problem|problem/\d*)/.+',
                            url) is not None
