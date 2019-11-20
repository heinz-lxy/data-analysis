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

数据采集代码见 [zhipin_crawl.py]()

使用关键词“数据分析”，对北上广深杭五个城市进行采集，其中杭州305条，广州300条，北京300条，上海295条，深圳300条，采集时间为2019年11月18日21点30分左右

![数据库](images\59298.jpg)

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

![列拆分](images\19977.jpg)

为了方便后续分析，将数据进行保存

    tb.save(r'data\%s.pkl'%city)

## 4数据分析
### 地区分布
按照地区进行分类汇总，并用漏斗图显示

    tb = Table(r'data\zhipin_hangzhou.pkl')
    tb.filter(tb.district!='不明').count_rank('district')\
    .to_frame().reset_index().funnel().render()

![地区分布](images\53935.jpg)

进一步绘制扇形图

    tb.filter(tb.district!='不明').count_rank('district')\
            .to_frame().pie(y=0).show()

![地区分布扇形图](images\52923.jpg)

可以看到西湖区作为“杭州数字经济第一区”绝不是浪得虚名的，和滨江、余杭区一起占据了岗位需求的3/4以上，另外除江干区外，萧山、拱墅、上城、下城几乎都可忽略不计


为了进一步分析，计算细化到镇、街道一级

![镇街分布](images\44195.jpg)


### 行业分布
对各行业的职位记录条数分组统计，并用漏斗图显示

    tb = Table(r'data\hangzhou.pkl')
    a = tb.count_rank('company_industry')
    a = a.reset_index()
    a.funnel().render()
![行业分布](images\59062.jpg)

### 经验分布
![经验分布](images\28365.jpg)

对比5-10年，3-5年，1-3年，及,可以看到对于新人的需求增量正在减少

新人（1年以内+经验不限+应届生）较其他经验组较需求较低，表明市场具有较强选择性，目前行业不处于爆发增长期

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

    db.run(sql.del_row('hz','publisher like "%人事%" or publisher like "%HR%"' or publisher like "%招聘%"' or publisher like "%人力%"'))
    a = db.run(sql.count('hz'))

    ((70,),)

计算得到人事人员在职位发布人中占比为 77.0%，可见“BOSS直聘”名不符实

hr更多只是用人部门的传话筒，那么谁是岗位背后的需求方呢？

![非人事招聘人](images\58548.jpg)

大致可以分为以下五类：

    1l老板、CEO、总经理
    2经理
    3主管
    4分析师
    5工程师

其中1、2属于公司管理层,4、5负责分析实现，3负责管理4、5，并对管理层负责


