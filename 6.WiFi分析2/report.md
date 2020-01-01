

上次针对时间段进行分析 了解到上班 上下班时间点 
由于上班时间具有星期的规律性，所以可对此进一步分析
tb = (
    Table(wifi()).transform('datetime',lambda x:
        t.parse_time(x,format='%Y/%m/%d %H:%M:%S')).dropna()
        .transform('datetime',lambda x:x.weekday())
)
tb.save('weekday.pkl')

tb = (
    Table('weekday.pkl')
    #.mean()
)
tb.delay = tb.delay.astype('int')
rst = tb.group('datetime').mean()
print(rst)


tb = (
    Table('weekday.pkl').dtype('int',['delay'])
    .group('datetime').mean().log()
    #.mean()
)


datetime            
0         262.485285
1         242.678608
2         286.055089
3         354.760123
4         263.667411
5         202.174398
6         191.882884

tb = (
    Table('weekday.pkl').dtype('int',['delay'])
    .group('datetime').mean().line()
)
tb.set_title('一周内网络活动变化情况')
tb.legend('延时')
tb.set_xticklabels(['','周一','周二','周三','周四','周五','周六','周日'])
# tb.save('weekday.pkl')
# print(tb.head(100))
plt.show()


在周四达到最高峰


周二到周四延迟持续上升
周四以后逐渐下滑

在周六周日达到最低谷

周日到周一有一个急剧上升，周二略有下降


周六周日与工作日明显差异   符合上班族特征
人群为 周末休息的上班族

工作日延迟高于休息日
可能是由于工作日上网时间集中在晚上，造成网络拥挤
而休息日上网时间较分散，使得延迟较低

在所有工作日中，周四达到最高值，或许因为此时是最后一个工作日前 夜晚，
一周工作压力积累达到最大
需要通过网络进行释放

在所有工作日中，周二出现延迟下滑
可能的原因为，经过周一的适应，重新开始适应工作的节奏，
同时紧张的工作还未完全展开



rst = (
    Table(wifi).transform('datetime',
        lambda dt_str:t.parse_time(dt_str,format='%Y/%m/%d %H:%M:%S'))
        .transfer('weekday','datetime',lambda dt:dt.weekday())
        .transfer('hour','datetime',lambda dt:dt.hour)
)
rst.save('gx3.pkl')
print(rst.head(2))
plt.show()


tb = Table('gx3.pkl')
rst = (
    tb.nan_clear().dtype('int',['weekday','hour']).dtype('float',['delay'])
        .get[tb.weekday==0,:]
        .group('hour').delay.mean()
)
rst = Column(rst).line()
rst.set_title('周一各时段延迟变化情况')
# print(rst)
plt.show()