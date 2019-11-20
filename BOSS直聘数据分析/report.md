## 1问题
### 背景
招聘信息纷繁错乱，男怕入错行

### 提出
区域分布规律如何？
行业分布规律如何？
经验分布规律如何？
学历分布规律如何？
薪酬分布规律如何？

不同城市间有何差异？（北上广深杭）

## 2数据来源

由于数据量不大，这里选择selenium模拟浏览器方法进行采集，实际过程中使用的是个人封装的库[browser.py](https://github.com/heinz-lxy/selenium-tools)

其中的Iterator类定义了浏览器翻页行为，在此基础上实现数据提取和数据库写入操作就基本完成了

[database.py](https://github.com/heinz-lxy/python-modules/blob/master/database.py) 对pymysql进行封装，并提供了sql语句模板函数

[excel.py](https://github.com/heinz-lxy/python-modules/blob/master/excel.py) 基于pandas进行封装，使用继承了DataFrame的Table类进行表格操作


        class ZhipinCrawler(IterateCrawler): 
        '''继承浏览器迭代操作类,完成boss直聘数据采集'''
            def __init__(self,page_count):
                super().__init__({'np_selector':'div.page>a.next'}, page_count)

            def extract(self): 
            '''对采集到的网页进行数据提取'''
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
            '''实现父类方法，采集完成后处理函数'''
                self.db.exit()
                t.say('job done')
            


使用关键词“数据分析”，对北上广深杭五个城市进行采集，其中杭州305条，广州300条，北京300条，上海295条，深圳300条，采集时间为2019年11月18日21点30分左右

## 3数据处理

### 去重
由于采集过程中可能存在重复，而且职位发布者可能重复发布相同岗位，所以需要去除重复项

    def unique(db, table):
    '''数据库记录去重'''
    db.clone(table,'tmp')
    db.run(sql.flush('tmp',sql.some(table,'distinct *')))
    db.run(sql.delete(table))
    db.run(sql.rename('tmp',table))


### 过滤
观察数据，发现记录中存在部分兼职岗位，需要去除，按照薪酬格式“xx/天”进行过滤

    for city in ['beijing','shanghai','guangzhou','shenzhen','hangzhou']:
    table = 'zhipin_%s'%city
    db = MySQL('job')
    db.run(sql.del_row(table,'salary like "%天"'))
    tb =  db.get(sql.all(table))

### 列拆分
观察数据，salary中包含了2个数值，分别为薪酬下限和上限，并且为文本格式，不符合分析要求
同样地，job_info为html字符串，需要对数据进行提取
另外，location中包含了3个地理层次，所以同样需要进行拆分

    #薪酬列拆分
    a = tb.salary.str.split('-',expand=True)
    tb['salary_low'] = a[0]
    tb['salary_high']= a[1].str.split('K',expand=True)[0]
    del tb['salary']
    tb.dtype('int',['salary_low','salary_high'])
    tb['salary_avg'] = (tb['salary_low']+tb['salary_high'])/2  #计算平均薪酬

    #地理信息列拆分
    c = tb.location.str.split(' ', expand=True)
    tb['district'] = c[1].apply(lambda x:x if x else '不明')
    tb['street'] = c[2].apply(lambda x:x if x else '不明')

    #职位信息列拆分
    b = tb.job_info.str.split('<em class="vline"></em>',expand=True)
    tb['location'] = b[0]
    tb['experience'] = b[1]
    tb['education'] = b[2]
    del tb['job_info']

处理完成后的效果：
![列拆分]()

为了方便后续分析，将数据进行保存

    tb.save(r'data\%s.pkl'%city)

## 4数据分析
### 地区分布
对地区进行排序并绘图
        
        tb.filter(tb.district!='不明').count_rank('district')\
                .to_frame().pie(y=0).show()

        tb.filter(tb.district!='不明').count_rank('district')\
        .to_frame().reset_index().funnel().render()


![地区分布](images\53935.jpg)

![镇街分布](images\44195.jpg)


可以看到西湖区作为“杭州数字经济第一区”绝不是浪得虚名的，和滨江、余杭区一起占据了岗位需求的3/4以上，另外除江干区外，萧山、拱墅、上城、下城几乎都可忽略不计

![](data\3数据分析\1地区分布\2.jpg)

### 行业分布
对各行业的职位记录条数分组统计，并用漏斗图显示

    tb = Table(r'data\hangzhou.pkl')
    a = tb.count_rank('company_industry')
    a = a.reset_index()
    a.funnel().render()
![行业分布](images\59062.jpg)

### 经验分布
![经验分布](images\28365.jpg)

对比5-10年，3-5年，1-3年，及（1年以内+经验不限+应届生),可以看到对于新人的需求增量正在减少

### 学历分布
    a = tb.count_rank('education')
    a = a.reset_index()
    a.pie2().render()
    print(a.columns)
![学历分布](images\91528.jpg)

### 经验薪酬相关性分析

以经验进行分组，计算平均岗位薪酬
        
    tb = Table(r'data\hangzhou.pkl')
    tb = tb.dtype('f8',['salary_avg'])
    a = tb.groupby('experience')['salary_avg'].mean().sort_values(ascending=True)

    experience
    1年以内      7.450000
    应届生       7.750000
    1-3年     12.073684
    经验不限     13.355263
    3-5年     18.837838
    5-10年    28.250000
    10年以上    30.000000

同样地，计算起薪和薪酬上限，得到

    1年以内      5.9-9K
    应届生       6-9.5K
    1-3年     9.1-15K
    经验不限     10-16.7K
    3-5年     14-23.7K
    5-10年    21-35.5K
    10年以上    20-40K

总体上薪酬可以分为5个等级，新人，1-3年（熟手），3-5年（骨干），5-10年（专家），10年以上（总监）

侧面反映出，当经验要求为不限时，用人单位的理想求职者经验为1-3年左右，并非真正岗位要求低

出现这种情况的原因可能有：

1.职位发布人比较懒或者是跟用人单位沟通不足，所以没有填写

2.对求职市场不够了解，为增加简历投递量便于筛选，降低求职者心理门槛

另外，在新人组内，应届生比经验1年内更高，可以看出看来boss们对萌新还是情有独钟

### 职位发布人分析
    db.run(sql.del_row('hz','publisher like "招聘%"'))
    tb = db.get(sql.all('hz','publisher'))
  
          publisher
    0            人事
    1            HR
    2          HRBP
    3          行政人事
    4        策略运营主管
    5          行政人事
    6            HR
    7         数据分析师
    8            HR
    9            HR
    10           人事
    11           HR
    12           HR
    13           HR
    14           HR
    15     大数据开发工程师
    16        数据分析师
    17         人事经理
    18         HRBP
    19         运营经理
    20         人事主管
    21         人事专员
    22          HRM

db.run(sql.del_row('hz','publisher like "人事%" or publisher like "HR%"'))

    db.run(sql.del_row('hz','publisher like "%人事"'))
    a = db.run(sql.count('hz'))

    ((70,),)

%人事%
%人力%
%HR%
%招聘%

boss直聘名不符实

    （305-70）/305=  77.0%


    hr只是用人部门的传话筒，那么实际的是那些人呢


[非人事招聘人]
大致可以分为以下五类：
1CEO、总经理
2经理
3主管
4分析师
5工程师

其中1、2属于公司管理层,4、5负责分析实现，3负责管理4、5，并对管理层负责


### 噱头
对岗位薪资中带有“xx薪”的进行筛选，发现几乎所有相应岗位发布者都是人事。

         tb = db.get(sql.some('zhipin6','publisher','salary like "%薪"'))
         print(tb)

![](data\3数据分析\噱头\2.jpg)

### 互联网公司最爱噱头
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
    
值得注意的是，在采集上海数据过程中，多次出现字段长度超过设定的情形，毕竟是国际大都市
pymysql.err.DataError: (1406, "Data too long for column 'company_name' at row 1")