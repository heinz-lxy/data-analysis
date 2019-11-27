# -*- coding: utf-8 -*-
# @Author: de retour
# @Date:   2019-11-18 19:04:43
# @Last Modified by:   de retour
# @Last Modified time: 2019-11-20 09:58:57

from browser import IterateCrawler
from database import MySQL
from database import sql
import re
import datetime
import t

class ZhipinCrawler(IterateCrawler):
    '''继承浏览器迭代操作类,完成boss直聘数据采集'''
    def __init__(self, page_count):
        template = {
            'np_selector':'div.page>a.next',
        }
        super().__init__(template, page_count)

    def extract(self):
        '''对采集到的网页进行数据提取'''
        self.db = MySQL('job')
        jobs = self.findall('div.job-list>ul>li')
        for job in jobs:
            title = self.find('.job-title',job).text
            salary = self.find('.red',job).text

            job_link = self.find('.info-primary>h3.name>a',job).get_attribute('href')
            job_id = re.search(r'/job_detail/(.*).html',job_link).group(1)
            job_info = self.find('.info-primary>p',job).get_attribute('innerHTML')

            company_name = self.find(".info-company>div>h3>a",job).text
            company_link = self.find(".info-company>div>h3>a",job).get_attribute('href')
            company_id = re.search(r'/gongsi/(.*).html',company_link).group(1)

            html_str = self.find('.company-text>p',job).get_attribute('innerHTML')
            company_info = html_str.split('''<em class="vline"></em>''')
            company_industry = company_info[0]
            company_size = company_info.pop()
            publisher = self.find('.info-publis>h3',job).get_attribute('innerHTML').split('<em class="vline"></em>').pop()
            date_str = self.find('.info-publis p',job).text
            date_str = date_str.split('发布于')[1]
            try:
                pub_date = datetime.datetime.strptime(date_str,'%m月%d日')
                pub_date = pub_date.replace(year = 2019)
            except ValueError:
                pub_date = datetime.datetime.strptime('11月18日','%m月%d日')
                pub_date = pub_date.replace(year = 2019)
            data = dict(title=title,salary=salary,job_info=job_info.replace('\"','\''),job_id=job_id,company_name=company_name\
                ,company_id=company_id,company_industry=company_industry,company_size=company_size\
                ,publisher=publisher,pub_date=str(pub_date))
            self.write(data)

    def write(self, data):
        '''将提取到的数据写入到数据库'''
        self.db.run(sql.append('zhipin_guangzhou',data))

    def next_page(self):
        '''重写父类方法，实现翻页操作'''
        url = self.instance.current_url
        rst = re.search(r'page=([0-9]*)&',url)
        match = rst.group()
        num = int(rst.group(1))
        self.to(url.replace(match,'page=%d&'%(num+1)))

    def after(self):
        '''实现父类方法，采集完成后处理函数'''
        self.db.exit()
        t.say('job done')

if __name__ == '__main__':
    zc = ZhipinCrawler(1000)
    zc.start(1)
    zc.run()