# -*- coding: utf-8 -*-
import json
from urllib.parse import unquote, urlencode

import scrapy

from waimai import settings
from waimai.items import ElemeBaseInfoItem
from waimai.mysqlhelper import *


class ElemeBaseInfoSpider(scrapy.Spider):
    """从搜索页爬取商家的基本信息

    从数据库提取尚爬取的坐标点，拼接url，添加到start_urls中
    对于每次爬取，从中提取出每个商家信息，交给pipeline
    如果当前坐标点还有其他商家未获取，则offset加上30，重新爬取
    """
    name = "eleme_base_info"
    allowed_domains = ["ele.me"]
    base_url = "https://mainsite-restapi.ele.me/shopping/restaurants" + "?extras[]=activities&extras[]=flavors&"

    def start_requests(self):
        start_urls = []
        # 饿了么的搜索页面每页最多30个商家，并且每个搜索组合只能获取最多750个
        params = {
            "latitude": "",
            "longitude": "",
            "offset": 0,
            "limit": 30,
            "order_by": 5  # order_by=5表示按商家距离排序
        }
        cur.execute("SELECT latitude, longitude FROM all_points WHERE status IS NULL")
        geo_data = cur.fetchall()
        for geo_point in geo_data:
            params["latitude"], params["longitude"] = geo_point
            yield scrapy.Request(self.base_url + urlencode(params))

    def parse(self, response):
        jsondata = json.loads(response.text)
        for restaurant_data in jsondata:
            item = ElemeBaseInfoItem()
            item_fields = item.fields.keys()
            restaurant_data.pop("distance")
            for key in restaurant_data.keys():
                if "id" == key:
                    item["restaurant_id"] = restaurant_data["id"]
                elif "type" == key:
                    item["restaurant_type"] = restaurant_data["type"]
                elif key in item_fields:
                    item[key] = restaurant_data[key]
            yield item

        # 提取URL参数
        params = {}
        query = unquote(response.url).split("?")[1]
        for key_value in query.split("&"):
            key, value = key_value.split("=")
            if "extras[]" != key:
                params[key] = value

        if "720" != params["offset"] and 30 == len(jsondata):
            # 如果当前不是最后一页并且当前页面的商家数是30个，则当前坐标点（很可能）还有未爬取的商家
            params["offset"] = int(params["offset"]) + 30
            url = self.base_url + urlencode(params)
            yield scrapy.Request(url, self.parse)
        elif 200 == response.status:
            # 如果正常返回，并且已经没有没有未爬取的商家，则把坐标点已爬取状态设为“OK”
            sql = "UPDATE all_points SET status = 'OK' WHERE latitude = '%(latitude)s' AND longitude = '%(longitude)s'"
            cur.execute(sql % params)
            cnx.commit()
