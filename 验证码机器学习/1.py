# -*- coding: utf-8 -*-
# @Author: de retour
# @Date:   2019-11-27 16:22:08
# @Last Modified by:   de retour
# @Last Modified time: 2019-11-27 17:33:24
# -*- coding: utf-8 -*-
# @Author: de retour
# @Date:   2019-11-24 22:24:11
# @Last Modified by:   de retour
# @Last Modified time: 2019-11-24 22:47:34
from sklearn.neighbors import KNeighborsClassifier

import matplotlib.pyplot as plt
from excel import Table 
import t


tb = Table(r'data\data.xlsx')
tb = tb.range_columns().reset_index(drop=True)
train_data = tb.loc[:17,:1023].values
train_target = tb.loc[:17,1024].values

test_data = tb.loc[18:22,:1023].values
test_target = tb.loc[18:22,1024].values


training_accuracy = []
test_accuracy = []

#try KNN for diffrent k nearest neighbor from 1 to 15
neighbors_setting = range(1,15)

# for n_neighbors in neighbors_setting:
#     knn = KNeighborsClassifier(n_neighbors=n_neighbors)
#     knn.fit(train_data,train_target)
#     training_accuracy.append(knn.score(train_data, train_target))
#     test_accuracy.append(knn.score(test_data, test_target))
 
# plt.plot(neighbors_setting,training_accuracy, label='Accuracy of the training set')
# plt.plot(neighbors_setting,test_accuracy, label='Accuracy of the test set')
# plt.show()


model_knn = KNeighborsClassifier(n_neighbors=8)
model_knn.fit(train_data, train_target)


rst = model_knn.score(test_data,test_target)
print(rst)
# print(test_target)
# print(model_knn.predict(test_data))
