# -*- coding: utf-8 -*-
import base64
import json
import os
import random

import scrapy
from waimai.mysqlhelper import *
from waimai.settings import MEITUAN_QUAL_PIC_DIR, USER_AGENTS_LIST


class MeituanQualPicSpider(scrapy.Spider):
    name = 'meituan_qual_pic'
    allowed_domains = ['meituan.com']
    custom_settings = {"DOWNLOAD_DELAY": 0.15}
    HEADERS1 = {
        "Pragma": "no-cache",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Host": "i.waimai.meituan.com",
        "Upgrade-Insecure-Requests": "1"
    }

    def start_requests(self):
        cur.execute("SELECT restaurant_id, qual_pic_url FROM qual_info WHERE pic_status IS NULL")
        all_qual_info = cur.fetchall()
        random.shuffle(all_qual_info)
        for restaurant_id, qual_pic_url in all_qual_info:
            url_list = json.loads(base64.b64decode(qual_pic_url))
            pic_num = len(url_list)
            for i, url in enumerate(url_list):
                file_ext = url.split(".")[-1]
                headers1 = self.HEADERS1
                ua = random.choice(USER_AGENTS_LIST)
                headers1["User-Agent"] = ua
                meta = {
                    "restaurant_id": str(restaurant_id),
                    "pic_id": str(i),
                    "filename": "%s-%02d.%s" % (restaurant_id, i, file_ext),
                    "pic_num": pic_num
                }
                yield scrapy.Request(url, meta=meta, headers=headers1)

    def parse(self, response):
        filename = response.meta["filename"]
        full_filename = os.path.join(MEITUAN_QUAL_PIC_DIR, filename)
        restaurant_id = response.meta["restaurant_id"]
        if response.headers["Content-Type"].decode().startswith("image"):
            with open(full_filename, "wb") as f:
                f.write(response.body)
        for i in range(response.meta["pic_num"]):
            basename = "%s-%02d" % (response.meta["restaurant_id"], i)
            for (root, dirs, files) in os.walk(MEITUAN_QUAL_PIC_DIR):
                all_basename = [os.path.splitext(filename)[0] for filename in files]
                if basename not in all_basename:
                    return None
        sql = "UPDATE qual_info SET pic_status = 'OK' WHERE restaurant_id = '%s'"
        cur.execute(sql % restaurant_id)
        cnx.commit()



for (root, dirs, files) in os.walk(MEITUAN_QUAL_PIC_DIR):
    all_basename = [os.path.splitext(filename)[0] for filename in files]