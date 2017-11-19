# -*- coding: utf-8 -*-
import json

import scrapy

from waimai import settings
from waimai.items import ElemeMenuItem
from waimai.mysqlhelper import *


class ElemeMenuSpider(scrapy.Spider):
    """获取商家菜单信息

    获取尚未获取menu的商家ID，拼接URL构建start_urls
    把结果交给pipeline
    """
    name = "eleme_menu"
    allowed_domains = ["ele.me"]
    base_url = "https://www.ele.me/restapi/shopping/v2/menu?restaurant_id="

    def start_requests(self):
        cur.execute("""
            SELECT restaurant_id, longitude, latitude FROM restaurant_info
            LEFT JOIN (SELECT restaurant_id AS id FROM menu_info) AS t
            ON restaurant_info.restaurant_id = t.id
            WHERE t.id IS NULL
        """)
        for restaurant_info in cur.fetchall():
            x_shard = "x-shard:shopid=%s;loc=%s,%s" % restaurant_info
            url = self.base_url + str(restaurant_info[0])
            headers = {"x-shard": x_shard}
            yield scrapy.Request(url, headers=headers)

    def parse(self, response):
        if 200 == response.status:
            item = ElemeMenuItem()
            item["menu"] = response.text
            item["restaurant_id"] = response.url.split("=")[-1]
            yield item
