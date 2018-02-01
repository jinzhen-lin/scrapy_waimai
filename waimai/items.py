# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GeoPointsItem(scrapy.Item):
    latitude = scrapy.Field()
    longitude = scrapy.Field()


class ElemeBaseInfoItem(scrapy.Item):
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


class ElemeMenuItem(scrapy.Item):
    restaurant_id = scrapy.Field()
    menu = scrapy.Field()


class ElemeRatingScoresItem(scrapy.Item):
    restaurant_id = scrapy.Field()
    compare_rating = scrapy.Field()
    food_score = scrapy.Field()
    positive_rating = scrapy.Field()
    service_score = scrapy.Field()
    star_level = scrapy.Field()


class ElemeLocationItem(scrapy.Item):
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    district = scrapy.Field()
    address = scrapy.Field()


class MeituanBaseInfoItem(scrapy.Item):
    across_book_max_days = scrapy.Field()
    across_book_offset_days = scrapy.Field()
    ad_attr = scrapy.Field()
    ad_type = scrapy.Field()
    average_price_tip = scrapy.Field()
    avg_delivery_time = scrapy.Field()
    brand_type = scrapy.Field()
    buz_type = scrapy.Field()
    charge_info = scrapy.Field()
    delivery_type = scrapy.Field()
    discounts2 = scrapy.Field()
    invoice_min_price = scrapy.Field()
    invoice_support = scrapy.Field()
    is_favorite = scrapy.Field()
    min_price = scrapy.Field()
    month_sale_num = scrapy.Field()
    mt_delivery_time = scrapy.Field()
    mt_poi_id = scrapy.Field()
    name = scrapy.Field()
    new_promotion = scrapy.Field()
    origin_status = scrapy.Field()
    pic_url = scrapy.Field()
    pic_url_square = scrapy.Field()
    poi_type_icon = scrapy.Field()
    pre_book = scrapy.Field()
    priority = scrapy.Field()
    recommend_info = scrapy.Field()
    restaurant_id = scrapy.Field()
    sales = scrapy.Field()
    shipping_fee = scrapy.Field()
    shipping_fee_discount = scrapy.Field()
    shipping_time_info = scrapy.Field()
    shipping_time_x = scrapy.Field()
    sort_reason_tag = scrapy.Field()
    sort_reason_type = scrapy.Field()
    status = scrapy.Field()
    status_desc = scrapy.Field()
    support_coupon = scrapy.Field()
    support_pay = scrapy.Field()
    wm_poi_opening_days = scrapy.Field()
    wm_poi_score = scrapy.Field()
    wm_poi_view_id = scrapy.Field()


class MeituanMenuItem(scrapy.Item):
    restaurant_id = scrapy.Field()
    menu = scrapy.Field()