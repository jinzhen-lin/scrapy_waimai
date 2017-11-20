# -*- coding: utf-8 -*-
import json
import re

import scrapy

from waimai.items import MeituanMenuItem
from waimai.meituan_encryptor import MeituanEncryptor
from waimai.mysqlhelper import *


class MeituanMenuSpider(scrapy.Spider):
    name = "meituan_menu"
    allowed_domains = ["meituan.com"]
    base_url1 = "http://i.waimai.meituan.com/restaurant/"
    base_url2 = "http://i.waimai.meituan.com/ajax/v8/poi/food?_token="

    def start_requests(self):
        cur.execute("""
            SELECT restaurant_id FROM restaurant_info
            LEFT JOIN (SELECT restaurant_id AS id FROM menu_info) AS t
            ON restaurant_info.restaurant_id = t.id
            WHERE t.id IS NULL
        """)
        for restaurant_id in cur.fetchall():
            url = self.base_url1 + str(restaurant_id[0])
            meta = {"cookiejar": restaurant_id[0]}
            yield scrapy.Request(url, meta=meta)

    def contruct_request(self, response, post_data=None):
        if post_data is not None:
            encryptor = MeituanEncryptor(post_data, response.url)
        else:
            encryptor = response.meta["encryptor"]
            post_data = encryptor.data

        token = encryptor.get_token(100010)
        url = self.base_url2 + token

        meta = {
            "encryptor": encryptor,
            "cookiejar": response.meta["cookiejar"]
        }
        return scrapy.FormRequest(
            url,
            meta=meta,
            formdata=post_data,
            callback=self.parse_menu
        )

    def parse(self, response):
        cookies_list = response.headers.getlist("Set-Cookie")
        uuid = [re.findall("w_uuid=(.*?);", x.decode()) for x in cookies_list]
        uuid = sum(uuid, [])[0]
        post_data = {
            "uuid": uuid,
            "platform": "3",
            "partner": "4",
            "wm_poi_id": response.url.split("/")[-1]
        }
        yield self.contruct_request(response, post_data)

    def parse_menu(self, response):
        try:
            jsondata = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            return self.contruct_request(response)

        item = MeituanMenuItem()
        item["restaurant_id"] = jsondata["data"]["poi_info"]["id"]
        item["menu"] = json.dumps(jsondata["data"]["food_spu_tags"], ensure_ascii=False)
        yield item
