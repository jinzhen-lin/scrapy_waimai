CREATE DATABASE eleme;
USE eleme;
CREATE TABLE all_points (
  latitude DOUBLE,
  longitude DOUBLE,
  status CHAR(5)
) ;


CREATE TABLE restaurant_info (
  restaurant_id BIGINT PRIMARY KEY,
  name TEXT,
  image_path CHAR(50),
  description TEXT,
  phone CHAR(100),
  restaurant_type CHAR(50),
  favored CHAR(5),
  flavors TEXT,
  is_new CHAR(5),
  is_premium CHAR(5),
  is_stock_empty CHAR(5),
  is_valid CHAR(5),
  regular_customer_count INT,
  recent_order_num INT,
  opening_hours CHAR(100),
  activities TEXT,
  promotion_info TEXT, 
  supports TEXT,
  district CHAR(30),
  address TEXT,
  address_baidu TEXT,
  latitude DOUBLE,
  longitude DOUBLE,
  delivery_mode TEXT,
  float_delivery_fee INT,
  float_minimum_order_amount INT,
  order_lead_time INT,
  rating DOUBLE,
  rating_count INT,
  compare_rating DOUBLE,
  food_score DOUBLE,
  positive_rating DOUBLE,
  service_score DOUBLE,
  star_level DOUBLE,
  max_applied_quantity_per_order INT,
  only_use_poi CHAR(5),
  piecewise_agent_fee TEXT,
  authentic_id BIGINT
) CHARSET=utf8;


CREATE TABLE menu_info (
  restaurant_id BIGINT PRIMARY KEY,
  menu MEDIUMTEXT
);