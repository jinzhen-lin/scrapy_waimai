# -*- coding: utf-8 -*-
import json
from urllib.parse import unquote, urlencode

import scrapy

from eleme import settings
from eleme.items import GeoPointsItem
from eleme.mysqlhelper import *


def get_allpoints(lat1, lng1, lat2, lng2, d_lat, d_lng, other_area=None, edge=False):
    all_lat = [lat1 + d_lat * i for i in range(int((lat2 - lat1) / d_lat))]
    all_lng = [lng1 + d_lng * i for i in range(int((lng2 - lng1) / d_lng))]
    if edge:
        all_lat.append(lat2)
        all_lng.append(lng2)
    points = [[i, j] for i in set(all_lat) for j in set(all_lng)]  # set为避免重复取点
    if other_area is not None:
        for area in other_area:
            lat1, lng1, lat2, lng2, d_lat, d_lng = area
            points_tmp = []
            for point in points:
                if not (lat1 <= point[0] <= lat2 and lng1 <= point[1] <= lng2):
                    points_tmp.append(point)
            points = points_tmp + get_allpoints(lat1, lng1, lat2, lng2, d_lat, d_lng, edge=edge)
    return points


class GeoPointsSpider(scrapy.Spider):
    """获取指定范围内属于某个市的点

    先通过指定的坐标范围与取点密度，获取所有坐标点，拼接URL
    再根据百度地图API的返回结果判断城市，如果是所需要的城市，则交给pipeline
    """

    name = "geo_points"
    custom_settings = {"DOWNLOAD_DELAY": 0}
    allowed_domains = ["baidu.com"]
    base_url = "http://api.map.baidu.com/geocoder/v2/?"

    def start_requests(self):
        params = {
            "coordtype": "gcj02ll",
            "location": "",
            "ak": settings.BAIDU_AK,
            "output": "json"
        }
        lat1, lng1, lat2, lng2, d_lat, d_lng = settings.POINTS_RANGE
        points = get_allpoints(
            lat1, lng1, lat2, lng2, d_lat, d_lng,
            other_area=settings.POINTS_OTHER_AREA,
            edge=settings.POINTS_AREA_EDGE
        )
        for point in points:
            params["location"] = "%s,%s" % (point[0], point[1])
            yield scrapy.Request(self.base_url + urlencode(params))

    def parse(self, response):
        jsondata = json.loads(response.text)
        item = GeoPointsItem()
        city = jsondata["result"]["addressComponent"]["city"]  # 从结果中提取城市名称
        if settings.POINTS_CITY == city:
            query = unquote(response.url).split("?")[1]
            for key_value in query.split("&"):
                key, value = key_value.split("=")
                if "location" == key:
                    item["latitude"], item["longitude"] = value.split(",")
            yield item
