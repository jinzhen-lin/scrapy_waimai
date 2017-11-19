# -*- coding: utf-8 -*-
import json

import scrapy

from waimai import settings
from waimai.items import ElemeRatingScoresItem
from waimai.mysqlhelper import *


class ElemeRatingScoresSpider(scrapy.Spider):
    """获取商家评分信息

    获取尚未爬取评分的商家ID，拼接URL构建start_urls
    把结果交给pipeline
    """
    name = "eleme_rating_scores"
    allowed_domains = ["ele.me"]
    base_url = "https://www.ele.me/restapi/ugc/v1/restaurants/%s/rating_scores?latitude=%s&longitude=%s"

    def start_requests(self):
        cur.execute("SELECT restaurant_id, latitude, longitude FROM restaurant_info WHERE compare_rating IS NULL")
        cnx.commit()
        for restaurant_location in cur.fetchall():
            yield scrapy.Request(self.base_url % restaurant_location)

    def parse(self, response):
        if 200 == response.status:
            item = ElemeRatingScoresItem()
            jsondata = json.loads(response.text)
            item["restaurant_id"] = response.url.split("/")[-2]
            for key in jsondata.keys():
                if key in item.fields.keys():
                    item[key] = jsondata[key]
            yield item
