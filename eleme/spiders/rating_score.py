# -*- coding: utf-8 -*-
import json
import urllib

import scrapy

from eleme import settings
from eleme.items import RatingScoresItem
from eleme.mysqlhelper import *


class RatingScoresSpider(scrapy.Spider):
    """获取商家评分信息
    
    获取尚未爬取评分的商家ID，拼接URL构建start_urls
    把结果交给pipeline
    """
    name = "rating_scores"
    allowed_domains = ["ele.me"]
    base_url = "https://www.ele.me/restapi/ugc/v1/restaurants/%s/rating_scores?latitude=%s&longitude=%s"
    cur.execute("SELECT restaurant_id, latitude, longitude FROM restaurant_info WHERE compare_rating IS NULL")
    cnx.commit()
    all_restaurant_location = cur.fetchall()
    start_urls = [base_url % i for i in all_restaurant_location]

    def parse(self, response):
        if 200 == response.status:
            item = RatingScoresItem()
            jsondata = json.loads(response.text)
            item["restaurant_id"] = response.url.split("/")[-2]
            for key in jsondata.keys():
                if key in item.fields.keys():
                    item[key] = jsondata[key]
            yield item
