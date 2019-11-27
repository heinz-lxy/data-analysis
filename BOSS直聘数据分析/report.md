## 1问题
### 提出
区域分布规律如何？
行业分布规律如何？
经验分布规律如何？
学历分布规律如何？
薪酬分布规律如何？

不同城市间有何差异？（北上广深杭）

## 2数据来源

由于数据量不大，这里选择selenium模拟浏览器方法进行采集（使用个人封装的[browser.py](https://github.com/heinz-lxy/selenium-tools)）

数据采集代码见 [zhipin_crawl.py]()

由于采集过程中可能存在重复，而且职位发布者可能重复发布相同岗位，所以需要去重（使用个人基于pymysql封装的[database.py](https://github.com/heinz-lxy/python-modules/blob/master/database.py) ，并提供了sql语句模板函数）

    def unique(db, table):
        '''数据库记录去重'''
        db.clone(table,'tmp')
        db.run(sql.flush('tmp',sql.some(table,'distinct *')))
        db.run(sql.delete(table))
        db.run(sql.rename('tmp',table))

采集站点为“BOSS直聘”，使用关键词“数据分析”，对北上广深杭五个城市进行，采集时间为2019年11月18日21点30分左右。最终获取到数据：杭州292条，广州300条，北京300条，上海295条，深圳300条（平台有数量限制）

![数据库](https://github.com/heinz-lxy/data-analysis/blob/master/BOSS%E7%9B%B4%E8%81%98%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90/images/59298.jpg?raw=true)

## 3数据处理
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

另外，location中包含了3个地理层次，所以同样需要进行拆分（使用的是[excel.py](https://github.com/heinz-lxy/python-modules/blob/master/excel.py) 基于pandas进行封装，使用继承了DataFrame的Table类进行表格操作）

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

![列拆分](https://github.com/heinz-lxy/data-analysis/blob/master/BOSS%E7%9B%B4%E8%81%98%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90/images/19977.jpg?raw=true)

为了方便后续分析，将数据进行保存

    tb.save(r'data\%s.pkl'%city)

## 4数据分析
### 概览
加载数据并预览

    tb = Table('data\hangzhou.pkl')
    tb.describe().view()

![概览](https://github.com/heinz-lxy/data-analysis/blob/master/BOSS%E7%9B%B4%E8%81%98%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90/images/38420.jpg?raw=true)
从中可以得到：
杭州292条职位记录中，有287个实际岗位，96个职位名

来自200家招聘单位，分布在34个行业，位于杭州的9个区，34个街道、镇

其中互联网行业人才求职机会最多，100-499人中等规模的公司

招聘意愿最强，最受雇主欢迎的是本科毕业、具有3-5年工作经验的求职者


另外，发布时间分布在125个自然日中，代表这批数据的整体时间跨度超过4个月，存在滞后性
### 地区分布
按照地区进行分类汇总，并用漏斗图显示

    tb = Table(r'data\zhipin_hangzhou.pkl')
    tb.filter(tb.district!='不明').count_rank('district')\
    .to_frame().reset_index().funnel().render()

![地区分布](https://github.com/heinz-lxy/data-analysis/blob/master/BOSS%E7%9B%B4%E8%81%98%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90/images/53935.jpg?raw=true)

进一步绘制扇形图

    tb.filter(tb.district!='不明').count_rank('district')\
            .to_frame().pie(y=0).show()

![地区分布扇形图](https://github.com/heinz-lxy/data-analysis/blob/master/BOSS%E7%9B%B4%E8%81%98%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90/images/52923.jpg?raw=true)

大致可以分为3个梯队：

第一梯队：西湖，滨江

第二梯队：余杭，江干

第三梯队：上城，下城，拱墅，萧山

其中西湖区第一，在职位需求占比中达1/3，第三梯队四区的总和甚至没有超过江干区


为了进一步分析，计算细化到镇、街道一级
![镇街分布](https://github.com/heinz-lxy/data-analysis/blob/master/BOSS%E7%9B%B4%E8%81%98%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90/images/44195.jpg?raw=true)

### 行业分布
对各行业的职位记录条数分组统计，并用漏斗图显示

    tb = Table(r'data\hangzhou.pkl')
    a = tb.count_rank('company_industry')
    a = a.reset_index()
    a.funnel().render()
![行业分布](https://github.com/heinz-lxy/data-analysis/blob/master/BOSS%E7%9B%B4%E8%81%98%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90/images/59062.jpg?raw=true)

### 经验分布
![经验分布](https://github.com/heinz-lxy/data-analysis/blob/master/BOSS%E7%9B%B4%E8%81%98%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90/images/28365.jpg?raw=true)

对比5-10年，3-5年，1-3年，及,可以看到对于新人的需求增量正在减少

新人（1年以内+经验不限+应届生）较其他经验组较需求较低，表明市场具有较强选择性，目前行业不处于爆发增长期

### 学历分布
    a = tb.count_rank('education')
    a = a.reset_index()
    a.pie2().render()
![学历分布](https://github.com/heinz-lxy/data-analysis/blob/master/BOSS%E7%9B%B4%E8%81%98%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90/images/91528.jpg?raw=true)

### 薪酬分布
![核密度估计](https://github.com/heinz-lxy/data-analysis/blob/master/BOSS%E7%9B%B4%E8%81%98%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90/images/58186.jpg?raw=true)

可见在大部分雇主眼中，10k是低端和高端岗位的一个分水岭

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

1.职位发布人比较忘记填写或者是跟用人单位沟通不足，所以没有填写

2.对求职市场不够了解，给出大概一般区间

3.为增加简历投递量便于筛选，降低求职者心理门槛

另外，在新人组内，应届生比经验1年内更高，可以看出看来BOSS们对萌新还是情有独钟

### 行业薪酬分析
![杭州](https://github.com/heinz-lxy/data-analysis/blob/master/BOSS%E7%9B%B4%E8%81%98%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90/images/99917.jpg?raw=true)

不同城市行业发展不均衡，光看一个城市不能判断行业好坏，所以需要对“北上广深”另外四座城市进行分析

![北京](https://github.com/heinz-lxy/data-analysis/blob/master/BOSS%E7%9B%B4%E8%81%98%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90/images/99789.jpg?raw=true)
![上海](https://github.com/heinz-lxy/data-analysis/blob/master/BOSS%E7%9B%B4%E8%81%98%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90/images/21542.jpg?raw=true)
![广州](https://github.com/heinz-lxy/data-analysis/blob/master/BOSS%E7%9B%B4%E8%81%98%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90/images/14264.jpg?raw=true)
![深圳](https://github.com/heinz-lxy/data-analysis/blob/master/BOSS%E7%9B%B4%E8%81%98%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90/images/42039.jpg?raw=true)

对比发现，杭州各行业整体呈比较均衡的错位状态，公关会展有所突出

北京的新能源、社交网络、人力资源服务

上海各行业都相对平均，整体薪酬也不高，只有房地产行业一枝独秀

深圳分布形态与上海类似，服务业

广州的网络设备、水利、O2O行业薪酬最高，整体平均薪酬为5座城市中最低


绘制箱型图，进一步对比5座城市的薪酬高低

![箱型图](https://github.com/heinz-lxy/data-analysis/blob/master/BOSS%E7%9B%B4%E8%81%98%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90/images/93821.jpg?raw=true)

图中可以看出：

1杭州的上限值、上相邻值、上四分位数、中位数均大于其他四座城市，其中上相邻值明显超过第二位的北京

2下四分位数接近北京、上海、深圳

3下限值与北京、深圳接近

可以得出结论：杭州在中高端岗位上较北上广深有优势，特别是在高端岗位上(“数字经济第一城”的说法是有根据的)，而在中低端岗位中差异不明显

### 职位发布人分析


    db.run(sql.del_row('hz','publisher like "%人事%" or publisher like "%HR%"' or publisher like "%招聘%"' or publisher like "%人力%"'))
    a = db.run(sql.count('hz'))

    ((70,),)

在292条职位记录中，只有70条为用人单位实际发布

人事人员在发布人中占比高达 77.0%，可见“BOSS直聘”名不符实