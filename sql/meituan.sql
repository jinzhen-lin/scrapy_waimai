CREATE DATABASE meituan;
USE meituan;


CREATE TABLE all_points (
  latitude DOUBLE,
  longitude DOUBLE,
  status CHAR(5)
) ;


CREATE TABLE restaurant_info (
  across_book_max_days INT,
  across_book_offset_days INT,
  ad_attr TEXT,
  ad_type INT,
  average_price_tip CHAR(20),
  avg_delivery_time INT,
  avg_delivery_time_encoded CHAR(20),
  brand_type INT,
  buz_type INT,
  charge_info TEXT,
  delivery_type INT,
  discounts2 TEXT,
  invoice_min_price INT,
  invoice_support INT,
  is_favorite INT,
  min_price INT,
  min_price_encoded CHAR(20),
  month_sale_num INT,
  month_sale_num_encoded CHAR(20),
  mt_delivery_time CHAR(20),
  mt_poi_id INT,
  name TEXT,
  new_promotion INT,
  origin_status INT,
  pic_url CHAR(150),
  pic_url_square TEXT,
  poi_type_icon CHAR(150),
  pre_book INT, 
  priority INT,
  recommend_info TEXT,
  restaurant_id BIGINT PRIMARY KEY,
  sales INT,
  shipping_fee INT,
  shipping_fee_discount INT,
  shipping_fee_tip CHAR(50),
  shipping_time_info TEXT,
  shipping_time_x TEXT,
  sort_reason_tag TEXT,
  sort_reason_type INT,
  status INT,
  status_desc CHAR(10),
  support_coupon INT,
  support_pay INT,
  wm_poi_opening_days INT,
  wm_poi_score DOUBLE,
  wm_poi_view_id CHAR(50)
) CHARSET=utf8;


CREATE TABLE menu_info (
  restaurant_id BIGINT PRIMARY KEY,
  menu MEDIUMTEXT,
  special TEXT
) CHARSET=utf8;



CREATE TABLE qual_info (
  restaurant_id BIGINT PRIMARY KEY,
  qual MEDIUMTEXT,
  qual_pic_url TEXT
) CHARSET=utf8;