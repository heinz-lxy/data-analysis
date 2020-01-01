tb = Table(amazon)
rst = (
    tb.nan_count()#view()
)


asin              0
brand             0
title             0
url               0
image             0
rating            0
reviewUrl         0
totalReviews      0
prices          215


tb.nan_clear()


sku总数
tb.nan_clear().get[:,['asin','brand','rating','totalReviews','prices']]
    .count_rank('asin').total

品牌数
tb.nan_clear().get[:,['asin','brand','rating','totalReviews','prices']]
    .count_rank('brand').total

10
Samsung   264
Apple      94
Motorola   69
Nokia      31
HUAWEI     29
Xiaomi     27
Google     26
Sony       21
ASUS       11
OnePlus     5


最高评分 诺基亚 异常
Google    5.0     26
Motorola  5.0     69
Samsung   5.0    264
Sony      5.0     21
Xiaomi    5.0     27
HUAWEI    4.8     29
ASUS      4.5     11
OnePlus   4.2      5
Nokia     3.8     31


   tb.nan_clear().get[:,['asin','brand','rating','totalReviews','prices']]
    .dtype('float', ['rating'])
    .group('brand').rating.agg(['min','count']).sort_values(by='min',ascending=False)


最低评分
小米，诺基亚
          min  count
brand               
Xiaomi    3.8     27
Nokia     2.8     31
HUAWEI    2.6     29
Google    2.0     26
Sony      2.0     21
ASUS      1.8     11
Apple     1.0     94
Motorola  1.0     69
OnePlus   1.0      5
Samsung   1.0    264

平均评分
brand
Xiaomi      4.337037
HUAWEI      4.000000
ASUS        3.818182
Google      3.780769
Sony        3.719048
Samsung     3.620076
Motorola    3.569565
Apple       3.525532
Nokia       3.348387
OnePlus     3.100000


评论总量  间接反映销量
brand
Samsung     27066.0
Apple       10768.0
Motorola     5510.0
Nokia        3442.0
Google       3267.0
Xiaomi       2948.0
HUAWEI       2802.0
Sony         2538.0
ASUS          497.0
OnePlus       104.0

   tb.nan_clear().get[:,['asin','brand','rating','totalReviews','prices']]

    .dtype('float', ['rating','totalReviews'])
    .group('brand').totalReviews.sum().sort_values(ascending=False)
)
# rst.view()


品牌平均价格 苹果异常 配件?
                mean  count
brand                      
OnePlus   480.332000      5
Google    332.243077     26
Sony      331.853810     21
HUAWEI    263.071034     29
Samsung   260.069621    264
ASUS      255.801818     11
Apple     251.577128     94
Xiaomi    220.011481     27
Motorola  164.286667     69
Nokia     145.328387     31

