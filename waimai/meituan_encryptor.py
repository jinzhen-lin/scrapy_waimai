# -*- coding: utf-8 -*-
import base64
import json
import random
import re
import time
import zlib
from urllib.parse import urlencode

from Crypto.Cipher import AES

from scrapy.selector import Selector


class MeituanEncryptor():

    def __init__(self, data, url, ts):
        self.ts = ts
        self.data = data
        self.url = url
        brVD_list = [
            [320, 568], [414, 736], [375, 667],
            [768, 1024], [412, 732],
            [375, 812], [1024, 1366]
        ]
        self.brVD = random.choice(brVD_list)
        self.brR = [self.brVD, self.brVD, 24, 24]

    def get_sign(self):
        clean_data = {
            key: value
            for key, value in self.data.items()
            if key not in ["uuid", "platform", "partner"]
        }
        sign_data = []
        for key in sorted(clean_data.keys()):
            sign_data.append(key + "=" + str(clean_data[key]))
        sign_data = "&".join(sign_data)
        compressed_data = self.compress_data(sign_data)
        self.sign = compressed_data
        return compressed_data

    def compress_data(self, data):
        json_data = json.dumps(data, separators=(',', ':')).encode("utf-8")
        compressed_data = zlib.compress(json_data)
        base64_str = base64.b64encode(compressed_data).decode()
        return base64_str

    def get_token(self, rid=100009):
        token_data = {
            "ver": "1.0.6",
            "aM": "",
            "rId": rid,
            "ts": self.ts,
            "cts": round(time.time() * 1000),
            "brVD": self.brVD,
            "brR": self.brR,
            "bI": [self.url, ""],
            "mT": [],
            "kT": [],
            "aT": [],
            "tT": [],
            "sign": self.get_sign()
        }
        """
        key_order = [
            "rId", "ver", "ts", "cts", "brVD", "brR", "bI",
            "mT", "kT", "aT", "tT", "aM", "sign"
        ]
        token_data = OrderedDict(
            sorted(token_data.items(), key=lambda t: key_order.index(t[0]))
        )
        """
        compressed_data = self.compress_data(token_data)
        self.token = compressed_data
        return compressed_data

    def get_xforwith(self, html_text=None):
        if html_text is not None:
            sel = Selector(text=html_text)
            meta_content = sel.xpath("//meta")[-1].xpath("./@content").extract_first()
            aes_key = "".join([meta_content[i * 10] for i in range(16)])
            aes_key = aes_key.encode()
            self.aes_key = aes_key
        aes_key = self.aes_key
        aes_iv = aes_key
        aes_mode = AES.MODE_CBC
        aes_cryptor = AES.new(aes_key, aes_mode, aes_iv)
        data = {
            "ts": self.ts,
            "cts": round(time.time() * 1000),
            "brVD": self.brVD,
            "brR": self.brR,
            "aM": ""
        }
        json_data = json.dumps(data, separators=(",", ":")).encode()
        json_data = json_data + b"\r" * (16 - len(json_data) % 16)
        x_for_with = base64.b64encode(aes_cryptor.encrypt(json_data))
        return x_for_with

    def get_mta(self, cookies, ua):
        hash_data = "Netscape" + "undefined" + "zh-cn" + "iPhone"
        hash_data += ua
        hash_data += ("0" + "x".join([str(x) for x in self.brVD]))
        cookies = "; ".join(["%s=%s" % item for item in cookies.items()])
        hash_data += cookies
        hash_data += self.url
        i = 3
        j = len(hash_data)
        while i > 0:
            hash_data += str(i ^ j)
            i -= 1
            j += 1
        n = 0
        i = 0
        e = len(hash_data) - 1
        while e >= 0:
            i = ord(hash_data[e])
            n = (n << 6 & 268435455) + i + (i << 14)
            i = 266338304 & n
            if i != 0:
                n = n ^ i >> 21
            e -= 1

        time1 = str(round(time.time() * 1000))
        time2 = time1
        time3 = time2
        mta = ".".join([str(n), time1, time2, time3, "1"])
        return mta

    def get_lxsdk(self, ua):
        def get_part2():
            rnd_num = random.random()
            num = rnd_num
            result = "0"
            while num >= 1e-10:
                num = num * 16
                int_part = int(num)
                result += hex(int_part)[2:]
                num = num - int_part
            return result

        def get_part3(ua):
            result = 0
            split4_list = re.sub("(.{4})", "\\1\0", ua).rstrip("\0").split("\0")
            for part in split4_list:
                part_ascii = [ord(c) for c in part[::-1]]
                part_result = 0
                for i in range(len(part_ascii)):
                    part_result |= part_ascii[i] << 8 * i
                result = result ^ part_result
            return hex(result)[2:]

        screen = self.brVD
        part1 = hex(round(time.time() * 1000))[2:] + hex(200)[2:]
        part2 = get_part2()
        part3 = get_part3(ua)
        part4 = hex(screen[0] * screen[1])[2:]
        part5 = hex(round(time.time() * 1000))[2:] + hex(200)[2:]
        return "-".join([part1, part2, part3, part4, part5])

    def get_lxsdk_s(self):
        part_list = []
        part_list.append(hex(round(time.time() * 1000))[2:])
        for i in range(3):
            rnd_hexchr_list = []
            for j in range(3):
                rnd_hexchr = hex(round(1 + 65536 * random.random()))[3]
                rnd_hexchr_list.append(rnd_hexchr)
            part_list.append("".join(rnd_hexchr_list))
        return "-".join(part_list) + "%7C%7CNaN"
