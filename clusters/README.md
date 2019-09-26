# 天文坐标聚类算法

## 功能

从MYSQL数据库中读取 `tag为SUPERNOV` 的坐标(Ra, Decl)，将他们视作天体的经纬度坐标进行聚类——

维护一个天体坐标集合S，对于新来的坐标，在集合S中找寻距离最近的天体，如果该距离大于CRI指定的弧度，则该坐标作为一个新的天体，并加入集合S，否则该坐标作为之前天体的一个观测，不加入集合。

最终将所有天体存入数据库。

## 运行方式

使用如下命令运行该算法——

```
make
./main
```
