# -*- coding: utf-8 -*-
import base64
import json
import random
import time
import zlib
from urllib.parse import urlencode


class MeituanEncryptor():

    def __init__(self, data, url):
        self.data = data
        self.url = url
        self.brVD_list = [[414, 736], [375, 667], [768, 1024], [412, 732], ]
        self.brR_list = [
            [[414, 736], [414, 736], 24, 24],
            [[375, 667], [375, 667], 24, 24],
            [[768, 1024], [768, 1024], 24, 24],
            [[412, 732], [412, 732], 24, 24]
        ]

    def get_clean_data(self):
        clean_data = {
            key: value
            for key, value in self.data.items()
            if key not in ["uuid", "platform", "partner"]
        }
        return clean_data

    def get_sign(self):
        data = {
            key: value
            for key, value in self.get_clean_data().items()
            if key not in ["uuid", "platform", "partner"]
        }
        sign_data = urlencode(data).encode("utf-8")
        compressed_data = self.compress_data(sign_data)
        self.sign = compressed_data
        return compressed_data

    def compress_data(self, data):
        compressed_data = zlib.compress(data)
        base64_str = base64.b64encode(compressed_data).decode()
        return base64_str

    def get_token(self, rid=100009):
        token_data = {
            "rId": rid,
            "ts": round(time.time() * 1000),
            "cts": round(time.time() * 1000) + round(random.random() * 700),
            "brVD": random.choice(self.brVD_list),
            "brR": random.choice(self.brR_list),
            "bI": [self.url, self.url],
            "mT": [],
            "kT": "",
            "aT": "",
            "tT": "",
            "sign": self.get_sign()
        }
        token_data = json.dumps(token_data).encode("utf-8")
        compressed_data = self.compress_data(token_data)
        self.token = compressed_data
        return compressed_data
