# -*- coding: utf-8 -*-
# @Author: de retour
# @Date:   2019-11-02 12:11:04
# @Last Modified by:   de retour
# @Last Modified time: 2019-11-30 20:44:25
from excel import Table, Column
import matplotlib.pyplot as plt  
import mock as mk
import t

tb = (
    mk.sh()#.head(5)
    .set_index('Date')
    # ['license_issued'].line()
)

print(tb['lowest_price'].corr(tb['applicants']))
plt.show()
# print(tb)
