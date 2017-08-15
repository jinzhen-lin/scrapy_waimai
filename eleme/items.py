# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GeoPointsItem(scrapy.Item):
    latitude = scrapy.Field()
    longitude = scrapy.Field()


class BaseInfoItem(scrapy.Item):
    activities = scrapy.Field()
    address = scrapy.Field()
    authentic_id = scrapy.Field()
    delivery_mode = scrapy.Field()
    description = scrapy.Field()
    flavors = scrapy.Field()
    favored = scrapy.Field()
    float_delivery_fee = scrapy.Field()
    float_minimum_order_amount = scrapy.Field()
    image_path = scrapy.Field()
    is_new = scrapy.Field()
    is_premium = scrapy.Field()
    is_stock_empty = scrapy.Field()
    is_valid = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    max_applied_quantity_per_order = scrapy.Field()
    name = scrapy.Field()
    only_use_poi = scrapy.Field()
    opening_hours = scrapy.Field()
    order_lead_time = scrapy.Field()
    phone = scrapy.Field()
    piecewise_agent_fee = scrapy.Field()
    promotion_info = scrapy.Field()
    rating = scrapy.Field()
    rating_count = scrapy.Field()
    recent_order_num = scrapy.Field()
    regular_customer_count = scrapy.Field()
    restaurant_type = scrapy.Field()
    restaurant_id = scrapy.Field()
    supports = scrapy.Field()


class MenuItem(scrapy.Item):
    restaurant_id = scrapy.Field()
    menu = scrapy.Field()


class RatingScoresItem(scrapy.Item):
    restaurant_id = scrapy.Field()
    compare_rating = scrapy.Field()
    food_score = scrapy.Field()
    positive_rating = scrapy.Field()
    service_score = scrapy.Field()
    star_level = scrapy.Field()


class LocationItem(scrapy.Item):
    restaurant_id = scrapy.Field()
    district = scrapy.Field()
    address = scrapy.Field()
