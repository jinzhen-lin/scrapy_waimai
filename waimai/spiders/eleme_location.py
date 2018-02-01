# -*- coding: utf-8 -*-
import json
from urllib.parse import urlencode

import scrapy

from waimai import settings
from waimai.items import ElemeLocationItem
from waimai.mysqlhelper import *


class ElemeLocationSpider(scrapy.Spider):
    """获取商家所在的district（市辖区/县级市/县）

    从数据库提取尚未获取district的商家ID和位置，拼接URL构造请求
    从结果中提取坐标点对应的district和address，交给pipeline
    """
    name = "eleme_location"
    custom_settings = {"DOWNLOAD_DELAY": 0}
    allowed_domains = ["baidu.com"]
    base_url = "http://api.map.baidu.com/geocoder/v2/?"

    def start_requests(self):
        cur.execute("SELECT latitude, longitude FROM restaurant_info WHERE district IS NULL")
        cnx.commit()
        all_restaurant_location = cur.fetchall()
        params = {
            "location": "",
            "output": "json",
            "ak": settings.BAIDU_AK,
            "coordtype": "gcj02ll"
        }
        for geo_point in all_restaurant_location:
            params["location"] = "%s,%s" % (geo_point[0], geo_point[1])
            url = self.base_url + urlencode(params)
            yield scrapy.Request(url, meta={"geo_point": geo_point})

    def parse(self, response):
        jsondata = json.loads(response.text)
        item = ElemeLocationItem()
        address = jsondata["result"]["addressComponent"]
        item["district"] = address["city"] + address["district"]
        item["address"] = jsondata["result"]["formatted_address"]
        item["latitude"] = response.meta["geo_point"][0]
        item["longitude"] = response.meta["geo_point"][1]
        yield item
