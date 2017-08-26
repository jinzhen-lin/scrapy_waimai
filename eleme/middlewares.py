# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import random

from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

from eleme import settings


class ElemeDownloaderMiddleware(UserAgentMiddleware):
    """用于设置随机UA和代理IP的中间件
    
    本爬虫项目中需要爬的页面包括饿了么的网站和百度地图API
    饿了么有反爬，所以需要设置代理IP，顺便设置随机UA
    """
    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        ua = random.choice(settings.USER_AGENTS_LIST)
        request.headers.setdefault('User-Agent', ua)
        if "ele.me" == spider.allowed_domains[0] and settings.PROXY_ENABLED:
            request.meta["proxy"] = settings.PROXY_SERVER
            request.headers["Proxy-Authorization"] = settings.PROXY_AUTH


class ElemeSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
