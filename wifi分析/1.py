# -*- coding: utf-8 -*-
# @Author: de retour
# @Date:   2019-11-02 12:11:04
# @Last Modified by:   de retour
# @Last Modified time: 2019-11-18 09:36:48
from excel import Table
from excel import Column
import mock 
import t

import matplotlib.pyplot as plt 



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

ad()