# -*- coding: utf-8 -*-
import base64
import random

from eleme.useragent import USER_AGENTS_LIST

# Scrapy settings for eleme project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'eleme'

SPIDER_MODULES = ['eleme.spiders']
NEWSPIDER_MODULE = 'eleme.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'eleme (+http://www.yourdomain.com)'
USER_AGENT = random.choice(USER_AGENTS_LIST)

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 30

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.18
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch, br",
    "Accept-Language": "zh-CN,zh;q=0.8"
}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'eleme.middlewares.ElemeSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'eleme.middlewares.ElemeDownloaderMiddleware': 543,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}


# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'eleme.pipelines.ElemePipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


# Mysql Setting
MYSQL_HOST = '127.0.0.1'
MYSQL_DBNAME = 'eleme'
MYSQL_USER = 'root'
MYSQL_PASSWD = 'YOUR_MYSQL_PASSWORD'
MYSQL_PORT = 3306


# Retry Settings
RETRY_ENABLED = True
RETRY_TIMES = 5
RETRY_HTTP_CODES = [429, 430]


# Baidu Map API AK (http://lbsyun.baidu.com)
BAIDU_AK = "YOUR_BAIDU_AK"


# Abuyun Proxy Settings (https://www.abuyun.com/)
PROXY_ENABLED = True
PROXY_SERVER = "http://proxy.abuyun.com:9020"
PROXY_USER = "YOUR_ABUYUN_PROXY_USER" # 通行证书
PROXY_PASS = "YOUR_ABUYUN_PROXY_PASS" # 通行密钥
PROXY_AUTH = "Basic " + base64.b64encode(PROXY_USER + ":" + PROXY_PASS)


# Points Area Settings
# POINTS_CITY 所需要获取的城市
POINTS_CITY = "北京市"
# POINTS_RANGE 选取的坐标范围，里面的元素依次是最小纬度、最小经度、最大纬度、最大经度、纬度间隔、经度间隔
POINTS_RANGE = [39.45, 115.43, 41.06, 117.52, 0.01, 0.01]
# POINTS_OTHER_AREA 本项目允许坐标点由多个范围组成，或者不同范围使用不同的经度/纬度间隔
# 使用时再POINTS_OTHER_AREA 这个list中添加元素，每个元素为一个新区域，定义区域的规则与POINTS_RANGE相同
# 如果后面的与前面的区域有重叠，则后面的会覆盖前面的
POINTS_OTHER_AREA = [[39.84, 116.3, 40, 116.45, 0.003, 0.003]]
# POINTS_AREA_EDGE 如果按坐标范围规则无法取到最大纬度和经度上的点，那么是否添加这些点
POINTS_AREA_EDGE = True
