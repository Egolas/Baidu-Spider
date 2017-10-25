import random
import requests
from bs4 import BeautifulSoup
import threading


class BaiduSpider(object):
    dayHead = [r'sunarray', r'monarray', r'tuearray', r'wedarray', r'thuarray', r'friarray', r'satarray']
    heads = [{"Accept-Language": "zh-CN,zh;q=0.8",
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240'},
             {"Accept-Language": "zh-CN,zh;q=0.8",
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0'},
             {"Accept-Language": "zh-CN,zh;q=0.8",
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'},
             {"Accept-Language": "zh-CN,zh;q=0.8",
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36 OPR/37.0.2178.31'},
             {"Accept-Language": "zh-CN,zh;q=0.8",
              'User-Agent': 'Opera/9.80 (Windows NT 6.1) Presto/2.12.388 Version/12.16'},
             {"Accept-Language": "zh-CN,zh;q=0.8",
              'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36'}]

    def __init__(self, keyword, page_num=5):
        self.url = 'http://news.baidu.com/ns'
        self.keyword = keyword
        self.page_num = page_num;
        self.params = {'word': keyword, 'pn': '0', 'tn': 'news', 'from': 'news', 'cl': '2', 'ct': '1'}
        self.search_list = []
        self.news_page = []
        self.news_content = []
        self.lock = threading.Lock()
        self.done_page_number = 1
        self.f = None


    @staticmethod
    def get_response(input_url, try_time=1000, **kwargs):
        if 'session' in kwargs:
            s = kwargs.pop('session')
        else:
            s = requests.Session()
        r = None
        while try_time > 0:
            try:
                r = s.get(input_url, **kwargs)
                break
            except requests.exceptions.RequestException:
                try_time -= 1
        if try_time <= 0:
            try:
                s.get(input_url, **kwargs)
            except requests.exceptions.RequestException as error:
                raise Exception(error, "overtry")
        return r, s

    def get_html_tree(self, url=None, header=None, params=None):
        if header is None:
            header = self.heads[random.randint(0, len(self.heads) - 1)]

        try:
            resp, s = self.get_response(url, params=params, headers=header, cookies={}, timeout=50)
        except Exception as error:
            print(error.args[1])
            exit()

        try:
            soup = BeautifulSoup(resp.content, "lxml")
            return soup
        except Exception as error:
            print(error)
            return

    def run(self):
        with open('file.txt', 'w', encoding="utf-8") as self.f:
            threads = []
            for pn in [0 + x * 20 for x in range(self.page_num)]:
                print("\rgetting list " + str(1 + pn // 20) + '/' + str(self.page_num), end='')
                self.params['pn'] = str(pn)
                if len(threads) < 8:
                    t = threading.Thread(target=self.thread_get_news_list, args=(pn,))
                    threads.append(t)
                    t.start()
                else:
                    threads[0].join()
                    threads.pop(0)
                    t = threading.Thread(target=self.thread_get_news_list, args=(pn,))
                    threads.append(t)
                    t.start()

            for t in threads:
                t.join()

            print("")
            threads = []
            for soup in self.search_list:
                for result in soup.find_all('div', {'class': 'result'}):
                    if len(threads) < 32:
                        t = threading.Thread(target=self.thread_get_content, args=(result.h3.a['href'],))
                        threads.append(t)
                        t.start()
                    else:
                        threads[0].join()
                        threads.pop(0)
                        t = threading.Thread(target=self.thread_get_content, args=(result.h3.a['href'],))
                        threads.append(t)
                        t.start()

                for t in threads:
                    t.join()

    def thread_get_news_list(self, pn):
        para = self.params
        para['pn'] = pn
        self.search_list.append(self.get_html_tree(url=self.url, params=para))

    def thread_get_content(self, url):
        print("\rprocessing page " + str(self.done_page_number), end='')
        current_page = self.get_html_tree(url)
        content = current_page.find_all('p')
        self.lock.acquire()
        try:
            self.f.write("\n--------Article: " + str(self.done_page_number) + "--------\n")
            for line in content:
                p = line.string
                if (p != None):
                    self.f.write(line.string + '\n')
        finally:
            self.done_page_number += 1
            self.lock.release()


if __name__  == "__main__":
    baidu_s = BaiduSpider('十九大', page_num=40)