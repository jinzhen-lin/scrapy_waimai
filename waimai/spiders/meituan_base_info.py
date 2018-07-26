# -*- coding: utf-8 -*-
import json
import random
import re
import time
from urllib.parse import urlencode

import scrapy
from scrapy.http.cookies import CookieJar
from scrapy.shell import inspect_response
from twisted.web.http_headers import Headers as TwistedHeaders
from waimai import settings
from waimai.items import MeituanBaseInfoItem
from waimai.meituan_encryptor import MeituanEncryptor
from waimai.mysqlhelper import *
from waimai.settings import USER_AGENTS_LIST


class MeituanBaseInfoSpider(scrapy.Spider):
    TwistedHeaders._caseMappings.update({
        b"x-for-with": b"X-FOR-WITH"
    })
    name = "meituan_base_info"
    allowed_domains = ["meituan.com"]
    base_url1 = "http://i.waimai.meituan.com/home?lat=%s&lng=%s"
    base_url2 = "http://i.waimai.meituan.com/ajax/v6/poi/filter?_token=%s"

    HEADERS1 = {
        "Pragma": "no-cache",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Host": "i.waimai.meituan.com",
        "Upgrade-Insecure-Requests": "1"
    }

    HEADERS2 = {
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Host": "i.waimai.meituan.com",
        "Upgrade-Insecure-Requests": "1",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "http://i.waimai.meituan.com",
        "Referer": "",
        "X-Requested-With": "XMLHttpRequest",
        "X-FOR-WITH": ""
    }

    def start_requests(self):
        cur.execute("SELECT latitude, longitude FROM all_points WHERE status IS NULL")
        geo_data = cur.fetchall()
        random.shuffle(geo_data)
        for i, geo_point in enumerate(geo_data):
            meta = {
                "cookiejar": str(random.random()),
                "geo_point": geo_point,
                "home_url": self.base_url1 % geo_point
            }
            headers1 = self.HEADERS1
            ua = random.choice(USER_AGENTS_LIST)
            headers1["User-Agent"] = ua
            yield scrapy.Request(self.base_url1 % geo_point, meta=meta, headers=headers1)

    def contruct_request(self, response, post_data=None, cookies=None, next_page=False):
        if post_data is not None:
            ts = round(time.time() * 1000)
            time.sleep(random.random() / 5 + 0.1)
            geo_point = response.meta["geo_point"]
            sign_data = post_data
            encryptor = MeituanEncryptor(sign_data, response.url, ts)
            mta = encryptor.get_mta(cookies, response.request.headers["User-Agent"].decode())
            lxsdk = encryptor.get_lxsdk(response.request.headers["User-Agent"].decode())
            lxsdk_s = encryptor.get_lxsdk_s()
            cookies = {
                "__mta": mta,
                "_lxsdk_cuid": lxsdk,
                "_lxsdk": lxsdk,
                "_lxsdk_s": lxsdk_s
            }
            x_for_with = encryptor.get_xforwith(response.body).decode()
        else:
            encryptor = response.meta["encryptor"]
            if next_page:
                post_data = encryptor.data
                post_data["page_index"] = str(int(post_data["page_index"]) + 1)
                encryptor.data = post_data
            cookies = {}
            x_for_with = encryptor.get_xforwith().decode()

        token = encryptor.get_token()
        url = self.base_url2 % token
        meta = {
            "home_url": response.meta["home_url"],
            "encryptor": encryptor,
            "cookiejar": response.meta["cookiejar"],
            "geo_point": response.meta["geo_point"]
        }

        headers2 = self.HEADERS2
        headers2["User-Agent"] = response.request.headers["User-Agent"]
        headers2["Referer"] = response.url
        headers2["X-FOR-WITH"] = x_for_with
        return scrapy.FormRequest(
            url,
            headers=headers2,
            cookies=cookies,
            meta=meta,
            formdata=post_data,
            callback=self.parse_restaurant
        )

    def parse(self, response):
        cookiejar = CookieJar()
        cookiejar.extract_cookies(response, response.request)
        cookies = cookiejar._cookies["i.waimai.meituan.com"]["/"]
        cookies = {key: cookies[key].value for key in cookies}
        uuid = cookies["w_uuid"]
        if "post_data" in response.meta.keys():
            post_data = response.meta["post_data"]
        else:
            geo_point = response.meta["geo_point"]
            post_data = {
                "platform": "3",
                "partner": "4",
                "page_index": "0",
                "apage": "1",
                # "page_size": "30",
                "sort_type": "5",
                "lat": str(geo_point[0]),
                "lng": str(geo_point[1]),
                "mtsi_font_css_version": ""
            }
        post_data["uuid"] = uuid
        yield self.contruct_request(response, post_data, cookies)

    def parse_restaurant(self, response):
        inspect_response(response, self)
        try:
            jsondata = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            return self.contruct_request(response)

        if "poi_has_next_page" not in jsondata["data"].keys():
            headers0 = self.HEADERS1
            headers0["User-Agent"] = response.request.headers["User-Agent"]
            meta = {
                "home_url": response.meta["home_url"],
                "cookiejar": str(random.random()),
                "geo_point": response.meta["geo_point"],
                "post_data": response.meta["encryptor"].data
            }
            if int(meta["post_data"]["page_index"]) <= 5:
                yield scrapy.Request(
                    meta["home_url"], meta=meta, headers=headers0, dont_filter=True
                )
            else:
                sql = "UPDATE all_points SET status = 'PAGE6' WHERE latitude = '%s' AND longitude = '%s'"
                cur.execute(sql % response.meta["geo_point"])
                cnx.commit()
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
            sql = "UPDATE all_points SET status = 'OK' WHERE latitude = '%s' AND longitude = '%s'"
            cur.execute(sql % response.meta["geo_point"])
            cnx.commit()
