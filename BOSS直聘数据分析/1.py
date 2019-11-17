# -*- coding: utf-8 -*-
# @Author: de retour
# @Date:   2019-11-02 12:11:04
# @Last Modified by:   de retour
# @Last Modified time: 2019-11-17 13:45:57
from database import sql 
from database import MySQL
import excel as ec
import mock
import t

db = MySQL('job')
tb = db.get(sql.all('zhipin6'))
a = tb.salary.str.split('-',expand=True)
tb['salary_low'] = a[0]
tb['salary_high']= a[1].str.split('K',expand=True)[0]
del tb['salary']
b = tb.job_info.str.split('<em class="vline"></em>',expand=True)
tb['location'] = b[0]
tb['experience'] = b[1]
tb['education'] = b[2]
del tb['job_info']

c = tb.location.str.split(' ', expand=True)
tb['district'] = c[1].apply(lambda x:x if x else '不明')

tb = tb.dropna().dtype('int',['salary_low','salary_high'])

tb = tb.get('',['salary_low']).head().log()
# a = tb.loc[:,['salary_low']]
print(a)

# a = tb.count_rank('company_size')\
# .to_frame().reset_index().funnel().render()



t.st()
db = MySQL('job')
# tb = db.get(sql.some('zhipin6','company_industry','salary like "%薪"'))
# print(tb.count_rank('company_industry').head(10))

tb = db.get(sql.some('zhipin6','company_name,company_size','salary not like "%薪"'))
a = tb.count_rank('company_size')
print(a)
t.st()


# a = tb.filter(tb.district!='不明').count_rank('district')\
#     .to_frame().reset_index().funnel().render()



# tb.count_rank('location').log().to_frame().head(10).bar().show()
# print(a)
# tb.save('1.xlsx')

# c = ec.s2col(tb.group('company_industry').count()['title']).\
# to_frame().sort(0,'desc').head(10).bar().show()
# print(c)


def mass():
    pass
    # a = tb.groupby('company_industry').title.describe()
    # a = ec.df2tb(a).reset_index()


    # a['percent'] = a['unique']/a['count']

    # print(a.sort('percent','asc'))
    # t.st()

    # a = ec.df2tb(tb.loc[tb.title=='数据分析师']).unique().total




    # t.st()
    # a = ec.df2tb(tb.groupby(by='company_industry').company_name.count

    # ().to_frame()\
    #     ).sort('company_name','desc').bar().show()
    # print(a)




    # a = db.get(sql.select('zhipin','title, salary'))
    #     print(a.total)



    # a = tb.unique().groupby(by=['company_industry'])['experience'].value_counts

    # ()

    # # a = tb.q(tb.company_industry.isin(['互联网']))['experience'].value_counts

    # ()
    # a = a.to_frame()#save('3.xlsx')
    # a = ec.df2tb(a).to_excel('4.xlsx')


    # # t.st()
    # # a = ec.df2tb(tb.loc[tb.company_industry.isin(['计算机软件'])]).unique

    # ().total


# cv = canvas.Canvas()
# cv.pie(df.values,{
#     'labels': df.index
# })
# cv.show()
# cv.save('行业分布.png')

# print(b['title'].values)
# b.describe


