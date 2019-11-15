
import echarts
import excel as ec 
import mock 
import numpy as np 
import pandas as pd 
tb = mock.gdp()
tb.set_index('地区', inplace = True)
tb.totype('f8')

print(tb.info())

