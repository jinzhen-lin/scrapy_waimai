# -*- coding: utf-8 -*-
import json
from urllib.parse import urlencode

import scrapy

from eleme import settings
from eleme.items import LocationItem
from eleme.mysqlhelper import *


class LocationSpider(scrapy.Spider):
    """获取商家所在的district（市辖区/县级市/县）

    从数据库提取尚未获取district的商家ID和位置，拼接URL构建start_urls
    从结果中提取坐标点对应的district和address，交给pipeline
    """
    name = "location"
    custom_settings = {"DOWNLOAD_DELAY": 0}
    allowed_domains = ["baidu.com"]
    base_url = "http://api.map.baidu.com/geocoder/v2/?"

    def start_requests(self):
        cur.execute("SELECT restaurant_id, latitude, longitude FROM restaurant_info WHERE district IS NULL")
        cnx.commit()
        all_restaurant_location = cur.fetchall()
        params = {
            "location": "",
            "output": "json",
            "ak": settings.BAIDU_AK,
            "coordtype": "gcj02ll"
        }
        for geo_point in all_restaurant_location:
            params["location"] = "%s,%s" % (geo_point[1], geo_point[2])
            url = self.base_url + urlencode(params)
            yield scrapy.Request(url, meta={"restaurant_id": geo_point[0]})

    def parse(self, response):
        jsondata = json.loads(response.text)
        item = LocationItem()
        address = jsondata["result"]["addressComponent"]
        item["district"] = address["city"] + address["district"]
        item["address"] = jsondata["result"]["formatted_address"]
        item["restaurant_id"] = response.meta["restaurant_id"]
        yield item
