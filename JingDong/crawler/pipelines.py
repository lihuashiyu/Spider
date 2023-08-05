#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
================================================================================
    ProjectName   ：  Spyder
    FileName      ：  pipelines
    CreateTime    ：  2021-09-11 12:38:00
    Author        ：  Administrator
    Email         ：
    PythonCompiler：  3.9.5
    IDE           ：  PyCharm 2020.3.4
    Version       ：  1.0
    Description   ：  配置管道：将数据写入文件和 Mysql
================================================================================
"""

import pymysql
import logging
from .items import ProductItem, CommentItem
from scrapy.utils.project import get_project_settings


# 将获取的数据以 json 格式写入文件
class WriteDataPipeline:
    # 初始化文件写入路径：商品信息文件路径、用户评价文件路径
    def __init__(self, product_path, comment_path):                            # 初始化
        self.product_path = product_path                                       # 保存商品的文件路径
        self.comment_path = comment_path                                       # 保存用户评价的文件路径
        
    # 获取配置文件中的文件路径
    @classmethod
    def from_crawler(cls, crawler):                                            # 使用 scrapy 自带框架
        return cls(
                product_path=crawler.settings.get("PRODUCT_PATH"),             # 从 settings 中获取商品描述的文件路径
                comment_path=crawler.settings.get("COMMENT_PATH"),             # 从 settings 中获取用户评价的文件路径
        )
        
    # 打开文件写入
    def open_spider(self, spider):
        self.product_file = open(file=self.product_path, mode="w", encoding="utf-8")
        self.comment_file = open(file=self.comment_path, mode="w", encoding="utf-8")
        
    # 写入文件
    def process_item(self, item, spider):
        if isinstance(item, ProductItem):                                      # 若是商品描述实体类
            self.product_file.write(str(item))                                 # 则写入商品描述文件
        if isinstance(item, CommentItem):                                      # 若是用户商品评价实体类
            self.comment_file.write(str(item))                                 # 则写入用户评价文件
        else:                                                                  # 若都不是
            logging.info(f"不存在此{item}")                                    # 则记录日志
        logging.info(f"商品 {item['sku_id']} 的数据已经写入文件 ...... ")
        return item
        
    # 关闭写入文件
    def close_spider(self, spider):
        self.product_file.close()
        self.comment_file.close()
        
        
# 将获取的数据写入到 Mysql 数据库
class MysqlPipeline:
    # 初始化数据库连接参数：数据库地址、端口号、用户名、密码、数据库名、连接字符集
    def __init__(self, host, port, user, password, database, charset):
        self.host = host                                                       # Mysql IP 地址
        self.port = port                                                       # Mysql 端口号
        self.user = user                                                       # Mysql 用户名
        self.password = password                                               # Mysql 用户对应的密码
        self.database = database                                               # Mysql 数据库名
        self.charset = charset                                                 # Mysql 连接字符集
        
    # 获取配置文件中的参数
    @classmethod
    def from_crawler(cls, crawler):                                            # 从 settings Mysql 参数
        return cls(
            host=crawler.settings.get("MYSQL_HOST"),                           # 从 settings Mysql IP 地址
            port=crawler.settings.get("MYSQL_PORT"),                           # 从 settings Mysql 端口号
            user=crawler.settings.get("MYSQL_USER"),                           # 从 settings Mysql 用户名
            password=crawler.settings.get("MYSQL_PASSWORD"),                   # 从 settings Mysql 用户对应的密码
            database=crawler.settings.get("MYSQL_DB_NAME"),                    # 从 settings Mysql 数据库名
            charset=crawler.settings.get("MYSQL_CONNECT_CHARSET"),             # 从 settings Mysql 连接字符集
        )
        
    # 建立连接
    def open_spider(self, spider):
        self.connect = pymysql.connect(host=self.host, port=self.port, user=self.user,
                                       password=self.password, db=self.database,
                                       charset=self.charset)                   # 建立 Mysql 连接
        self.cursor = self.connect.cursor()                                    # 获取游标，用于执行 sql 
        
    # 写入数据
    def process_item(self, item, spider):
        settings = get_project_settings()                                      # 实例化 settings
        if isinstance(item, ProductItem):                                      # 若是商品描述实体类
            product_sql = settings["PRODUCT_SQL"]                              # 获取商品描述 sql
            transform = DictToString(item)                                     # 实例化字典的参数转换类
            product = transform.transform()                                    # 将字典中参数进行转换
            # 获取商品描述信息相关参数
            data_tuple = (product["sku_id"], product["store"], product["product_price"],
                          product["fans_price"], product["guide_price"],
                          product["original_price"], product["brand"],
                          product["description"], product["url"], product["comment_count_list"],
                          product["favorable_rate"], product["comment_target_list"],
                          product["show_picture_count"], product["show_video_count"],
                          product["add_comment_count"], product["better_comment_count"],
                          product["general_comment_count"], product["bed_comment_count"])
            self.cursor.execute(product_sql, data_tuple)                       # 执行 sql
        elif isinstance(item, CommentItem):
            comment_sql = settings["COMMENT_SQL"]                              # 获取用户评价信息 sql
            transform = DictToString(item)                                     # 实例化字典的参数转换类
            comment = transform.transform()                                    # 将字典中参数进行转换
            # 获取用户评价信息相关参数
            data_tuple = (comment["sku_id"], comment["user_id"], comment["user_guid"],
                          comment["user_name"], comment["user_head_url"], comment["user_level"],
                          comment["score"], comment["buy_time"], comment["comment_time"],
                          comment["item_description"], comment["content"], comment["imagine_count"],
                          comment["imagine_info_list"], comment["video_count"],
                          comment["video_info_list"], comment["like_count"],
                          comment["reply_count"], comment["add_comment_content"])
            self.cursor.execute(comment_sql, data_tuple)                       # 执行 sql
        else:                                                                  # 若都不是
            logging.info(f"不存在此{item}")                                    # 则记录日志
            
        logging.info(f"商品 {item['sku_id']} 的数据已经写 Mysql 数据库 ...... ")
        self.connect.commit()                                                  # 提交运行
        return item
    
    # 关闭连接
    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()
        
        
# 将字典中的的参数进行转换
class DictToString:
    # 初始化参数
    def __init__(self, object_dict):
        self.object_dict = object_dict
        
    # 将字典中的的参数进行转换
    def transform(self):
        result = {}
        key_list = self.object_dict.keys()                                     # 获取字典中的所有键
        for key in key_list:                                                   # 遍历每个键
            result[key] = str(self.object_dict[key])                           # 将字典中的所有值转为字符串
        return result
