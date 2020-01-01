# -*- coding: utf-8 -*-
# @Author: de retour
# @Date:   2019-12-12 22:42:14
# @Last Modified by:   de retour
# @Last Modified time: 2019-12-12 23:01:13

from excel import Table
from excel.dataset import wifi

tb = (
    Table(wifi()).log()
)