# -*- coding: utf-8 -*-
import json
import urllib

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
    start_urls = []
    cur.execute("SELECT restaurant_id, latitude, longitude FROM restaurant_info WHERE district IS NULL")
    cnx.commit()
    all_restaurant_location = cur.fetchall()
    params = {
        "location": "",
        "output": "json",
        "ak": settings.BAIDU_AK,
        "coordtype": "gcj02ll",
        "restaurant_id": ""  # 为了能从response中获取商家ID所以添加此参数，实际百度地图API无此参数，但能够正常返回结果
    }
    for geo_point in all_restaurant_location:
        params["location"] = "%s,%s" % (geo_point[1], geo_point[2])
        params["restaurant_id"] = geo_point[0]
        start_urls.append(base_url + urllib.urlencode(params))

    def parse(self, response):
        jsondata = json.loads(response.text)
        item = LocationItem()
        address = jsondata["result"]["addressComponent"]
        item["district"] = address["city"] + address["district"]
        item["address"] = jsondata["result"]["formatted_address"]
        query = urllib.unquote(response.url).split("?")[1]
        for key_value in query.split("&"):
            key, value = key_value.split("=")
            if "restaurant_id" == key:
                item["restaurant_id"] = value
        yield item
