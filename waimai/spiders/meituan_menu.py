# -*- coding: utf-8 -*-
import json
import random
import re
import time

import scrapy
from scrapy.http.cookies import CookieJar
from scrapy.shell import inspect_response
from twisted.web.http_headers import Headers as TwistedHeaders
from waimai.items import MeituanMenuItem
from waimai.meituan_encryptor import MeituanEncryptor
from waimai.mysqlhelper import *
from waimai.settings import MEITUAN_MAX_RETRY_TIMES, USER_AGENTS_LIST


class MeituanMenuSpider(scrapy.Spider):
    TwistedHeaders._caseMappings.update({
        b"x-for-with": b"X-FOR-WITH"
    })
    name = "meituan_menu"
    allowed_domains = ["meituan.com"]
    base_url1 = "http://i.waimai.meituan.com/restaurant/%s"
    base_url2 = "http://i.waimai.meituan.com/ajax/v8/poi/food?_token=%s"

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
        "Accept": "*/*",
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
        cur.execute("""
            SELECT restaurant_id FROM restaurant_info
            LEFT JOIN (SELECT restaurant_id AS id FROM menu_info) AS t
            ON restaurant_info.restaurant_id = t.id
            WHERE t.id IS NULL
        """)
        all_restaurants = cur.fetchall()
        random.shuffle(all_restaurants)
        for restaurant_id in all_restaurants:
            yield self.menu_pre_requests(restaurant_id)

    def menu_pre_requests(self, restaurant_id, retry_times=0):
        if retry_times > MEITUAN_MAX_RETRY_TIMES:
            return None
        if type(restaurant_id) == tuple:
            restaurant_id = str(restaurant_id[0])
        url = self.base_url1 % restaurant_id
        meta = {
            "cookiejar": restaurant_id,
            "retry_times": retry_times
        }
        headers1 = self.HEADERS1
        ua = random.choice(USER_AGENTS_LIST)
        headers1["User-Agent"] = ua
        return scrapy.Request(url, meta=meta, headers=headers1)

    def contruct_request(self, response, post_data=None, cookies=None):
        if post_data is not None:
            ts = round(time.time() * 1000)
            time.sleep(random.random() / 5 + 0.1)
            encryptor = MeituanEncryptor(post_data, response.url, ts)
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
            post_data = encryptor.data
            cookies = {}
            x_for_with = encryptor.get_xforwith().decode()

        token = encryptor.get_token(100010)
        url = self.base_url2 % token

        meta = {
            "encryptor": encryptor,
            "cookiejar": response.meta["cookiejar"],
            "retry_times": response.meta["retry_times"]
        }
        headers2 = self.HEADERS2
        headers2["User-Agent"] = response.request.headers["User-Agent"]
        headers2["Referer"] = response.url
        headers2["X-FOR-WITH"] = x_for_with
        return scrapy.FormRequest(
            url,
            headers=headers2,
            meta=meta,
            cookies=cookies,
            formdata=post_data,
            callback=self.parse_menu
        )

    def parse(self, response):
        cookiejar = CookieJar()
        cookiejar.extract_cookies(response, response.request)
        if "i.waimai.meituan.com" not in cookiejar._cookies.keys():
            yield self.menu_pre_requests(
                response.meta["cookiejar"],
                response.meta["retry_times"] + 1
            )
            return None
        cookies = cookiejar._cookies["i.waimai.meituan.com"]["/"]
        cookies = {key: cookies[key].value for key in cookies}
        uuid = cookies["w_uuid"]
        post_data = {
            "uuid": uuid,
            "platform": "3",
            "partner": "4",
            "wm_poi_id": response.meta["cookiejar"]
        }
        yield self.contruct_request(response, post_data, cookies)

    def parse_menu(self, response):
        #inspect_response(response, self)
        try:
            jsondata = json.loads(response.text)
        except json.decoder.JSONDecodeError:
            return self.contruct_request(response)

        if response.text.find("account/login?backurl") != -1:
            yield self.menu_pre_requests(
                response.meta["cookiejar"],
                response.meta["retry_times"] + 1
            )
            return None

        item = MeituanMenuItem()
        try:
            item["restaurant_id"] = jsondata["data"]["poi_info"]["id"]
            # inspect_response(response, self)
            item["menu"] = json.dumps(jsondata["data"]["food_spu_tags"], ensure_ascii=False)
            if "container_operation_source" in jsondata["data"].keys():
                item["special"] = json.dumps(jsondata["data"]["container_operation_source"], ensure_ascii=False)
            yield item
        except TypeError:
            inspect_response(response, self)
