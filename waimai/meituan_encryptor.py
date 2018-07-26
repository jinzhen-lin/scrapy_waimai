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

    def compress_data(self, data):
        """压缩token和sign参数的方法
        转为JSON字符串，使用zlib压缩，再使用base64编码
        """
        json_data = json.dumps(data, separators=(',', ':')).encode("utf-8")
        compressed_data = zlib.compress(json_data)
        base64_str = base64.b64encode(compressed_data).decode()
        return base64_str

    def get_sign(self):
        """构造sign（请求的URL中一个参数）
        由各种乱七八糟的信息组成的字典，进行URL编码，URL参数拼接，然后压缩
        """
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

    def get_token(self, rid=100009):
        """构造_token（请求的URL中一个参数）
        由各种乱七八糟的信息（包括sign)组成的字典，转为JSON字符串后压缩
        """
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
        compressed_data = self.compress_data(token_data)
        self.token = compressed_data
        return compressed_data

    def get_xforwith(self, html_text=None):
        """构造X-FOR-WITH（headers中的一项）
        将时间、屏幕像素等多种信息组成的字典（见以下data变量）转为JSON字符串
        然后使用AES加密，AES加密模式为CBC
        加密的密钥和IV一样，构造方式为：
        一开始进入的网页里有个meta元素（一般为页面最后一个meta元素了），id为六位随机字母组成
        取其content（很长），然后从第0个字符开始，每10个取一个字符，最多取16个字符）
        """
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
        """构造__mta（cookies中的一项）
        第一部分：把各种信息的字符串拼起来，然后进行一些神奇的hash处理
        第二部分-第四部分：由三个时间戳组成，具体哪个代表什么不大清楚，但可以都一样
        第五部分：从1开始，会随着时间增长一直加，不过就按1来吧
        以上五部分使用"."来拼接
        """
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
        """构造_lxsdk_cuid和_lxsdk（两者一样，都是cookie中的一项）
        由五部分组成，各部分之间用"-"连接
        第一部分：时间戳转16进制，字符串再接上200转16进制的字符串
        第二部分：0-1之间的随机数，转16进制小数，去掉小数点
        第三部分：User-Agent字符串每四位分段，然后进行一些神奇的处理
        第四部分：屏幕总像素数量转16进制
        第五部分：时间戳转16进制，字符串再接上200转16进制的字符串
        """

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
        """构造_lxsdk_s（cookies中的一项）
        第一部分是时间戳转16进制字符串
        第二部分-第四部分都是由三个字符组成，每个字符是1-65537之间的随机数
        转16进制后取第一位（相当于随机16进制字符吧）
        这四部分用"-"连接，之后又加上"//NaN"（反正每次都是以这个结尾，要URL编码）
        """
        part_list = []
        part_list.append(hex(round(time.time() * 1000))[2:])
        for i in range(3):
            rnd_hexchr_list = []
            for j in range(3):
                rnd_hexchr = hex(round(1 + 65536 * random.random()))[2]
                rnd_hexchr_list.append(rnd_hexchr)
            part_list.append("".join(rnd_hexchr_list))
        return "-".join(part_list) + "%7C%7CNaN"
