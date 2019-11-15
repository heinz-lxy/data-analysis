# -*- coding: utf-8 -*-
# @Author: de retour
# @Date:   2019-10-29 18:51:55
# @Last Modified by:   de retour
# @Last Modified time: 2019-10-30 09:19:24
from database import MySQL
import excel as ec 
import canvas

db = MySQL('job')
df = db.get('select * from zhipin_job')

df = df.groupby('company_industry').count()

print(df)




# cv = canvas.Canvas()
# cv.pie(df.values,{
#     'labels': df.index
# })
# cv.show()
# cv.save('行业分布.png')

# print(b['title'].values)
# b.describe


