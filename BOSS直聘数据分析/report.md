# BOSS直聘"数据分析"岗位分析

# 0准备
[browser.py](https://github.com/heinz-lxy/selenium-tools)
对selenium模拟浏览器进行封装

[database.py](https://github.com/heinz-lxy/python-modules/blob/master/database.py) 对pymysql进行封装，并提供了sql语句模板

[excel.py](https://github.com/heinz-lxy/python-modules/blob/master/excel.py) 基于pandas进行封装，使用继承了DataFrame的Table类进行表格操作


# 1获取数据
由于数据量不大，这里使用模拟浏览器方法进行爬取
IterateBrowser类定义了浏览器翻页行为，在此基础上实现数据提取和数据库写入操作就基本完成了

        class ZhipinCrawler(IterateCrawler): 
        '''继承浏览器迭代操作类,完成boss直聘数据爬取'''
            def __init__(self,page_count):
                super().__init__({'np_selector':'div.page>a.next'}, page_count)

            def extract(self): 
            '''对爬取到的网页进行数据提取'''
                self.db = database.MySQL('job')
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
                        pub_date = datetime.datetime.now()
                    self.write(title,salary,job_info,job_id,company_name,company_id,\
                        company_industry,company_size,publisher,pub_date)

            def write(self,title,salary,job_info,job_id,company_name,company_id,\
                        company_industry,company_size,publisher,pub_date):
            '''将提取到的数据写入到数据库'''
                sql = """insert into zhipin_job(title,salary,job_info,job_id,company_name,company_id,\
                        company_industry,company_size,publisher,pub_date) \
                    values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')""" % \
                    (title,salary,job_info,job_id,company_name,company_id,\
                        company_industry,company_size,publisher,pub_date)
                self.db.execute(sql)

            def next_page(self):
            '''重写父类方法，实现翻页操作'''
                url = self.instance.current_url
                rst = re.search(r'page=([0-9]*)&',url)
                match = rst.group()
                num = int(rst.group(1))
                self.open(url.replace(match,'page=%d&'%(num+1)))

            def after(self):
            '''实现父类方法，爬取完成后处理函数'''
                self.db.exit()
                t.say('job done')
            
数据采集于boss直聘，使用关键词为“数据分析”，城市范围为“杭州”，采集时间为2019年11月8日

# 2数据处理
由于爬取过程中可能存在重复，并且职位发布者可能重复发布相同岗位，所以需要去除重复项

        #数据库去重
        db = MySQL('job')
        db.clone('zhipin','zhipin2')
        db.run(sql.flush('zhipin2',sql.some('zhipin','distinct *')))

## 2.1薪酬信息处理

观察数据后发现薪酬分为全职和兼职两种， 兼职岗位为xx/天，而部分全职岗位后面为xx薪

首先过滤掉兼职类岗位

        db.run(sql.count('zhipin6'))  #302
        db.run(sql.del_row('zhipin6','salary like "%天"'))
        db.run(sql.count('zhipin6'))  #285

然后进行列拆分

这里使用了pandas的StringMethod方法

        db = MySQL('job')
        tb = db.get(sql.all('zhipin'))
        a = tb.salary.str.split('-',expand=True)
        tb['salary_low'] = a[0]
        tb['salary_high']= a[1].str.split('K',expand=True)[0]
        del tb['salary']

处理完成后的效果：

![](data\2数据处理\1.jpg)

## 2.2位置信息处理

对采集到的job_info进行拆分
        b = tb.job_info.str.split('<em class="vline"></em>',expand=True)
        tb['location'] = b[0]
        tb['experience'] = b[1]
        tb['education'] = b[2]
        del tb['job_info']
![](data\2数据处理\3.jpg)

对location列进一步拆分

        c = tb.location.str.split(' ', expand=True)
        tb['district'] = c[1].apply(lambda x:x if x else '不明')
![](data\2数据处理\4.png)
![](data\2数据处理\5.png)

# 3数据分析
## 3.1地区分布
对地区进行排序并绘图
        
        tb.filter(tb.district!='不明').count_rank('district')\
                .to_frame().pie(y=0).show()

        tb.filter(tb.district!='不明').count_rank('district')\
        .to_frame().reset_index().funnel().render()

![](data\3数据分析\1地区分布\3.jpg)
可以看到西湖区作为“杭州数字经济第一区”绝不是浪得虚名的，和滨江、余杭区一起占据了岗位需求的3/4以上，另外除江干区外，萧山、拱墅、上城、下城几乎都可忽略不计

![](data\3数据分析\1地区分布\2.jpg)

## 3.2行业分布
![](data\3数据分析\2行业分布\2.jpg)

## 3.4经验分布
![](data\3数据分析\4经验分布\2.jpg)

对比5-10年，3-5年，1-3年，及（1年以内+经验不限+应届生),可以看到对于新人的需求增量正在减少
## 3.4招聘研究

### 3.4.1噱头
对岗位薪资中带有“xx薪”的进行筛选，发现几乎所有相应岗位发布者都是人事。

         tb = db.get(sql.some('zhipin6','publisher','salary like "%薪"'))
         print(tb)

![](data\3数据分析\噱头\2.jpg)

### 3.4.2互联网公司最爱噱头
对数量进行统计

        a = db.run(sql.count('zhipin6'))[0][0]
        b = db.run(sql.count('zhipin6','salary like "%薪"'))[0][0]
        print(b/a)  #0.3298245614035088
结果：0.3298245614035088
33.0%，近1/3比重


难道其他非人事发布的岗位的福利就很一般吗？
筛选不含“薪”的岗位对应公司和规模，并进行统计

        tb = db.get(sql.some('zhipin6','company_name,company_size','salary not like "%薪"'))
        a = tb.count_rank('company_size')
        print(a)

        company_size（salary not like "%薪"）
        100-499人      57
        20-99人        45
        1000-9999人    42
        500-999人      23
        10000人以上      13
        0-20人          8


        company_size（salary like "%薪"）
        1000-9999人    32
        100-499人      27
        500-999人      18
        20-99人         9
        10000人以上       7
        0-20人          1
进行对比发现，整体上含“薪”的公司规模更大



        tb = db.get(sql.some('zhipin6','title,company_industry','salary like "%薪"'))
        print(tb.count_rank('title').head(10))


        数据分析师          40
        数据分析            5
        数据分析专家          4
        数据分析员           3
        数据分析工程师         3
        Python数据分析师     3
        数据分析主管          3
        数据分析专员          2
        商业数据分析师         2
        数据分析专家（BI）      1


不出意外地，“数据分析师”作为高大上的营销概念拔得头筹，甩开第二名不止十条街

再对“数据分析”对应的公司规模进行查询

        tb = db.get(sql.some('zhipin6','company_size','title="数据分析师"'))
        print(tb.count_rank('company_size').head(10))

        
        100-499人      41
        1000-9999人    29
        20-99人        24
        500-999人      14
        0-20人          4
        10000人以上       3

考虑到越大规模的公司数量越少，基本可以得出中大型公司HR更善于使用营销概念吸引求职者，而考虑到中小公司HR入职门槛较低，更可以得出不善于营销的HR不是好的HR结论


可见“xx薪”更多是公司HR人员招聘的营销招聘手段，实际意义并不大。



    




