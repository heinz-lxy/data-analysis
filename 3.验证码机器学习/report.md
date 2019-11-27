# 验证码识别机器学习
## 问题
在使用爬虫进行数据采集时，经常遇到验证码，使得采集无法继续进行。这时往往会使用切换IP代理的方式绕过验证，缺点在于需要维护一个IP代理池。

如果能通过程序自动识别出验证码的内容就好了！

## 数据收集
这里使用验证码的验证码来自[http://shuicao.cc/member.php?mod=register](http://shuicao.cc/member.php?mod=register)

## 数据处理
由于验证码图片尺寸较小，这里使用的是KNN分类算法，将图片的像素值平铺作为特征向量

为了突出问题解决性，降低不必要的复杂度，这里将图片中的字符进行手工分割，得到单个字符
![字符分割](https://github.com/heinz-lxy/data-analysis/blob/master/3.%E9%AA%8C%E8%AF%81%E7%A0%81%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0/images/49216.jpg?raw=true)

为了进一步降低复杂度，这里仅选取2、3、4这三个字符进行测试

## 特征向量化

    img_dict = {}
    for file in t.files():
        if(file.find('png')<0):
            continue
        im = cv2.imread(file,cv2.IMREAD_GRAYSCALE)
        img_dict[file] = im.flatten()
    tb = Table(img_dict).T
    tb.save('data.xlsx')

    [[[154 152 162]
      [153 150 161]
      [152 150 161]
      ...
      [125 128 145]
      [126 129 145]
      [124 128 144]]]

得到的是这样的矩阵，使用每个像素点包含了RGB三个分量。考虑到验证码对颜色信息不敏感，并且为了提高算法处理速度，以灰度图形式载入图片
    
    im = cv2.imread(file,cv2.IMREAD_GRAYSCALE)

于是得到

    [[156 154 154 ... 139 139 139]
     [150 149 149 ... 134 133 132]
     [150 149 149 ... 133 134 133]
     ...
     [150 150 149 ... 133 133 133]
     [151 150 150 ... 134 133 133]
     [150 150 149 ... 133 134 133]]

## 数据标注
将图片放入对应数字的文件夹，统一编号。为了保证算法的公平性，训练集中每一类保持数量相同
![图片分类](https://github.com/heinz-lxy/data-analysis/blob/master/3.%E9%AA%8C%E8%AF%81%E7%A0%81%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0/images/72041.jpg?raw=true)

由于图片分类后排列有序，标注时只需下拉复制即可

![数据标注](https://github.com/heinz-lxy/data-analysis/blob/master/3.%E9%AA%8C%E8%AF%81%E7%A0%81%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0/images/30120.jpg?raw=true)
## 模型训练
载入训练集

    tb = Table(r'data\data.xlsx')
    tb = tb.range_columns().reset_index(drop=True)
    train_data = tb.loc[:53,:1023].values
    train_target = tb.loc[:53,1024].values
    test_data = tb.loc[54:59,:1023].values
    test_target = tb.loc[54:59,1024].values

分别测试1-15的近邻数

    training_accuracy = []
    test_accuracy = []
    for n_neighbors in range(1,15) :
        knn = KNeighborsClassifier(n_neighbors=n_neighbors)
        knn.fit(train_data,train_target)
        training_accuracy.append(knn.score(train_data, train_target))
        test_accuracy.append(knn.score(test_data, test_target))
    plt.plot(neighbors_setting,training_accuracy, label='训练集准确度')
    plt.plot(neighbors_setting,test_accuracy, label='测试准确度')
    plt.legend()
    plt.show()

![邻近数测试](https://github.com/heinz-lxy/data-analysis/blob/master/3.%E9%AA%8C%E8%AF%81%E7%A0%81%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0/images/12386.png?raw=true)

可以看到，在k=1时，训练集和测试集的准确度都达到最高值，所以将k选定为1
    
    model_knn = KNeighborsClassifier(n_neighbors=1)
    model_knn.fit(train_data, train_target)

## 评估
    print(test_target)
    print(model_knn.predict(test_data))

    [4 3 2 2 3 2]
 ![测试集](https://github.com/heinz-lxy/data-analysis/blob/master/3.%E9%AA%8C%E8%AF%81%E7%A0%81%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0/images/92749.png?raw=true)


可以看到模型计算的结果和实际基本符合，进一步计算准确率

    rst = model_knn.score(test_data,test_target)
    print(rst) 

得到准确率为83.3%
    

