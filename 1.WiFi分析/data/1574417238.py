# -*- coding: utf-8 -*-
# @Author: de retour
# @Date:   2019-11-02 12:11:04
# @Last Modified by:   de retour
# @Last Modified time: 2019-11-22 18:24:07
from excel import Table, Column
import mock
import t

tb = mock.wifi2()
print(tb.total)


# tb['weekday'] = 
tb['datetime'] = Column(tb.datetime).to_datetime(errors='coerce')
tb['weekday'] = tb.datetime.apply(lambda x:x.weekday())
del tb['datetime']
tb.save('data_weekday.pkl')

