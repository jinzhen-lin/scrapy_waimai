# -*- coding: utf-8 -*-
import json
import re
from urllib.parse import urlencode

import scrapy

from waimai import settings
from waimai.items import MeituanBaseInfoItem
from waimai.meituan_encryptor import MeituanEncryptor
from waimai.mysqlhelper import *


class MeituanBaseInfoSpider(scrapy.Spider):
    name = "meituan_base_info"
    allowed_domains = ["meituan.com"]
    base_url1 = "http://i.waimai.meituan.com/home?"
    base_url2 = "http://i.waimai.meituan.com/ajax/v6/poi/filter?_token="

    def start_requests(self):
        params = {}
        cur.execute("SELECT latitude, longitude FROM all_points WHERE status IS NULL")
        geo_data = cur.fetchall()
        for i, geo_point in enumerate(geo_data):
            params["lat"], params["lng"] = geo_point
            urlparams = urlencode(params)
            meta = {
                "cookiejar": i,
                "geo_point": params
            }
            yield scrapy.Request(self.base_url1 + urlparams, meta=meta)

    def contruct_request(self, response, post_data=None, next_page=False, other_info=None):
        if post_data is not None:
            encryptor = MeituanEncryptor(post_data, response.url)
        else:
            encryptor = response.meta["encryptor"]
            post_data = encryptor.data
            if next_page:
                post_data["page_index"] = str(int(post_data["page_index"]) + 1)
                encryptor.data = post_data

        token = encryptor.get_token()
        url = self.base_url2 + token

        meta = {
            "encryptor": encryptor,
            "cookiejar": response.meta["cookiejar"],
            "geo_point": response.meta["geo_point"],
            "other_info": other_info if other_info is not None else {}
        }
        return scrapy.FormRequest(
            url,
            meta=meta,
            formdata=post_data,
            callback=self.parse_restaurant
        )

    def parse(self, response):
        cookies_list = response.headers.getlist("Set-Cookie")
        uuid = [re.findall("w_uuid=(.*?);", x.decode()) for x in cookies_list]
        uuid = sum(uuid, [])[0]
        post_data = {
            "uuid": uuid,
            "platform": "3",
            "partner": "4",
            "page_index": "0",
            "apage": "1",
            "page_size": "300",
            "sort_type": "5"
        }
        yield self.contruct_request(response, post_data)

    def parse_restaurant(self, response):
        try:
            jsondata = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            return self.contruct_request(response)

        if jsondata["code"] == 406:
            other_info = response.meta["other_info"]
            if "retry_times" not in other_info.keys():
                other_info["retry_times"] = 0
            if other_info["retry_times"] >= settings.MEITUAN_RETRY_TIMES:
                raise scrapy.exceptions.CloseSpider("爬虫已被美团发现，请更换IP")
            other_info["retry_times"] += 1
            yield self.contruct_request(response, other_info=other_info)
            return None

        for restaurant_data in jsondata["data"]["poilist"]:
            item = MeituanBaseInfoItem()
            item_fields = item.fields.keys()
            restaurant_data["restaurant_id"] = restaurant_data["id"]
            for key in restaurant_data.keys():
                if key in item_fields:
                    item[key] = restaurant_data[key]
            yield item

        if jsondata["data"]["poi_has_next_page"]:
            yield self.contruct_request(response, next_page=True)
        elif 200 == response.status:
            # 如果正常返回，并且已经没有没有未爬取的商家，则把坐标点已爬取状态设为“OK”
            sql = "UPDATE all_points SET status = 'OK' WHERE latitude = '%(lat)s' AND longitude = '%(lng)s'"
            cur.execute(sql % response.meta["geo_point"])
            cnx.commit()
