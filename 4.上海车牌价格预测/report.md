# 上海车牌价格预测
tb = Table(sh)
rst = (
    tb.get[tb.Date.str.match('.*Sep'),:]
    .get[:,['Date','avg_price']]
    .extract('year','Date','-',0)
)



print(rst)
plt.show()

tb = Table(sh)
rst = (
    tb.get[tb.Date.str.match('.*Sep'),:]
    .get[:,['Date','avg_price']]
    .extract('year','Date','-',0)
    .dtype('int',['year'])
    
)
# rst.line(x='year',y='avg_price')
# rst.set_title('2012-2018年上海车牌平均价格走势(9月)')
# 

x = rst.year.values.reshape((-1, 1))
y = rst.avg_price.values

model = LinearRegression()
model.fit(x, y)
print(model.score(x,y))

0.854224448503401


model = LinearRegression()
model.fit(x, y)
import numpy as np
print(model.predict(np.array([19]).reshape((-1, 1))))

[93859.72794118]
9月份
