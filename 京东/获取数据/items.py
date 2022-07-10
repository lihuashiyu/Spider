#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
================================================================================
    ProjectName   ：  Spyder
    FileName      ：  items
    CreateTime    ：  2021-09-11 12:38:00
    Author        ：  Administrator
    Email         ：
    PythonCompiler：  3.9.5
    IDE           ：  PyCharm 2020.3.4
    Version       ：  1.0
    Description   ：  商品字段信息
================================================================================
"""

from scrapy import Item, Field


# 商品描述和评价数据
class ProductItem(Item):
    # 商品数据
    store = Field()                              # 店铺名称
    # store_star = Field()                       # 店铺评分
    sku_id = Field()                             # 商品 ID
    product_price = Field()                      # 商品价格
    fans_price = Field()                         # 商品粉丝价格
    guide_price = Field()                        # 商品指导价
    original_price = Field()                     # 商品原价
    # ship_address = Field()                     # 发货地址
    brand = Field()                              # 品牌
    description = Field()                        # 商品详细参数介绍
    url = Field()                                # 商品详情页链接
    # 用户评论                                   
    comment_count_list = Field()                 # 全部评价数量
    favorable_rate = Field()                     # 好评度
    comment_target_list = Field()                # 评价标签
    show_picture_count = Field()                 # 晒图数量
    show_video_count = Field()                   # 视频晒单数量
    add_comment_count = Field()                  # 追评数量
    better_comment_count = Field()               # 好评数量
    general_comment_count = Field()              # 中评数量
    bed_comment_count = Field()                  # 差评数量
                                                 
                                                 
# 用户对商品的评论数据                           
class CommentItem(Item):                         
    sku_id = Field()                             # 商品 ID
    user_id = Field()                            # 用户 ID
    user_guid = Field()                          # 用户 GUID
    user_name = Field()                          # 用户名字
    user_head_url = Field()                      # 用户头像 url
    user_level = Field()                         # 用户等级
    score = Field()                              # 评分
    buy_time = Field()                           # 购买时间
    comment_time = Field()                       # 留言时间
    item_description = Field()                   # 商品描述
    content = Field()                            # 评论内容
    imagine_count = Field()                      # 图片数量
    imagine_info_list = Field()                  # 图片信息
    video_count = Field()                        # 视频数量
    video_info_list = Field()                    # 视频信息
    like_count = Field()                         # 点赞数
    reply_count = Field()                        # 回复数
    add_comment_content = Field()                # 追评
