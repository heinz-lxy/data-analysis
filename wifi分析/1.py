# -*- coding: utf-8 -*-
# @Author: de retour
# @Date:   2019-11-02 12:11:04
# @Last Modified by:   de retour
# @Last Modified time: 2019-11-17 21:54:03
from excel import Table
from excel import Column
import mock 
import t

import matplotlib.pyplot as plt 

tb = Table('delay.txt', sep = '\s{1,}')
# print(tb['delay'].sort_values(ascending=False).pct_change())
a = tb.reset_index().sort_values(by='hour',ascending=True).set_index('hour').pct_change()
a['delay'] 
a.plot()
plt.show()
# Column(tb.set_index('hour')['freq']).line().show()