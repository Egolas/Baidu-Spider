
from BaiduSpider import BaiduSpider

print("请输入关键词")

s = BaiduSpider('共享单车', page_num=40)
s.run()