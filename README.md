# 基于Scrapy的饿了么外卖平台商家信息爬虫

## 爬虫思路
饿了么上只能通过指定的位置信息来获取该位置附近的商家，并且无论附近商家有多少，最多只能获取750个，所以采取密集取坐标点获取商家信息的策略。


## 依赖
- Python 2.7
- Scrapy: `pip install scrapy`
- MySQL
- mysql-connector-python: `pip install mysql-connector-python-rf`
- [百度地图API](http://lbsyun.baidu.com/)：最好申请开发者认证，每天配额和每分钟最大并发量比较大。

此外，为了应对饿了么的反爬虫，最好准备一个代理方式，否则就要把下载延迟设置得比较长。可以先从网上搜集免费的代理，然后每次发送请求随机选择代理，但比较不稳定。也可以选择一些云代理服务，稳定些不过要付费。本项目使用的是[阿布云代理](https://www.abuyun.com/)的动态版，虽然默认每秒最多只能使用五次但勉强也不算太少。如果使用其他的需要自己改代码(修改`eleme/middlewares.py`中的`ElemeDownloaderMiddleware`，或者另外写一个中间件并在`eleme/setting.py`中设置)。


## 使用方法
先运行 eleme.sql 中的sql代码来创建数据库和表，然后根据自己的实际情况和需要修改setting.py中的设置，然后就可以使用`scrapy crawl <spider_name>`（`<spider_name>`为爬虫名称）来运行相应的爬虫。项目中共包含五个爬虫，并且有一定的运行顺序要求。

- geo_points: 根据经纬坐标范围和密度生成若干坐标点，并用百度地图API筛选出指定城市的点。这个要第一个运行，因为正式爬取需要基于这些坐标点。
- base_info: 根据坐标点进行搜索，获取商家（部分）信息。这个要第二个运行，后面三个需要利用到这个爬虫获取的数据。
- rating_scores: 获取商家评分
- menu: 获取商家菜单
- location: 利用百度地图API获取商家位置信息

后面三个爬虫互不影响，可以根据实际是否需要这部分数据来决定是否运行。