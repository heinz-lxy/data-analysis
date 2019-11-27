# -*- coding: utf-8 -*-
# @Author: de retour
# @Date:   2019-11-02 12:11:04
# @Last Modified by:   de retour
# @Last Modified time: 2019-11-22 18:37:04
from excel import Table
from excel import Column
import mock 
import t

import matplotlib.pyplot as plt 

tb = Table(r'data\data_weekday.pkl')
tb = tb.dtype('f8', ['delay'])
a = tb.groupby('weekday')['delay'].mean().reset_index()

b = tb[0]
print(b)


#    weekday       delay
# 0      0.0  262.485285
# 1      1.0  242.678608
# 2      2.0  286.055089
# 3      3.0  355.251976
# 4      4.0  263.667411
# 5      5.0  202.174398
# 6      6.0  191.882884


def ad():
    tb = Table('delay.txt', sep = '\s{1,}')
    # print(tb['delay'].sort_values(ascending=False).pct_change())
    tb = tb.reset_index()
    tb = tb.dtype('f8',['delay'])
    tb = tb.dtype('int',['hour'])
    a = tb.sort_values(by='hour',ascending=True).set_index('hour')
    # a['delay'] 
    a.plot()
    plt.show()
    # Column(tb.set_index('hour')['freq']).line().show()

