# 基于Scrapy的饿了么和美团外卖平台商家信息爬虫

**规则已失效，且不再更新，代码仅供参考**


## 爬虫思路
饿了么/美团外卖上只能通过指定的位置信息来获取该位置附近的商家，所以采取密集取坐标点获取商家信息的策略。


## 依赖
- Python 3.6
- Scrapy: `pip install scrapy`
- MySQL
- mysql-connector-python: `pip install mysql-connector-python-rf`
- [百度地图API](http://lbsyun.baidu.com/)：最好申请开发者认证，每天配额和每分钟最大并发量比较大。

此外，为了应对反爬虫，最好准备一个代理方式，否则就要把下载延迟设置得比较长。可以先从网上搜集免费的代理，然后每次发送请求随机选择代理，但比较不稳定。也可以选择一些云代理服务，稳定些不过要付费。本项目使用的是[阿布云代理](https://www.abuyun.com/)的动态版，虽然默认每秒最多只能使用五次但勉强也不算太少。如果使用其他的需要自己改代码(修改`eleme/middlewares.py`中的`ElemeDownloaderMiddleware`，或者另外写一个中间件并在`eleme/setting.py`中设置)。


## 使用方法
先运行 `sql/eleme.sql`（或`sql/meituan.sql`) 中的sql代码来创建数据库和表，然后根据自己的实际情况和需要修改`setting.py`中的设置，然后就可以使用`scrapy crawl <spider_name>`（`<spider_name>`为爬虫名称）来运行相应的爬虫。项目中包含的爬虫有一定的运行顺序要求。




- geo_points: 根据经纬坐标范围和密度生成若干坐标点，并用百度地图API筛选出指定城市的点。这个要第一个运行，因为正式爬取需要基于这些坐标点。注意要根据要爬的网站通过设置`setting.py`进行数据库名称选择。

- 之后根据要爬的网站(eleme或者meituan)运行`eleme_base_info`或者`meituan_base_info`，这两个爬虫用于遍历坐标点获取所有商家的基本信息（虽说是基本信息不过已经相当全了）

- 其他爬虫可以根据自己需要以任意顺序运行，以`eleme_`和`meituan_`开头的爬虫分别属于饿了么外卖和美团外卖部分。



## 注意事项

为了避免各种编码问题以及JSON字符串的引号等问题，爬虫在将数据存入数据库前先对JSON字符串进行了BASE64编码，所以在使用数据前需要现将相应的字符串进行BASE64解码

此项目的爬虫在上传至github前有可能已失效（未验证），项目仅供学习交流使用。


