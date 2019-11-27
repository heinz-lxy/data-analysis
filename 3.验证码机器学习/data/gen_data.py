# -*- coding: utf-8 -*-
# @Author: de retour
# @Date:   2019-11-27 15:55:55
# @Last Modified by:   de retour
# @Last Modified time: 2019-11-27 16:15:06
import cv2
from excel import Table
import t 


img_dict = {}
for file in t.files():
    if(file.find('png')<0):
        continue
    im = cv2.imread(file,cv2.IMREAD_GRAYSCALE)
    img_dict[file] = im.flatten()
tb = Table(img_dict).T
tb.save('data.xlsx')