#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
================================================================================
    ProjectName   ：  Spyder
    FileName      ：  JingDong
    CreateTime    ：  2021-09-11 12:38:00
    Author        ：  Administrator
    Email         ：
    PythonCompiler：  3.9.5
    IDE           ：  PyCharm 2020.3.4
    Version       ：  1.0
    Description   ：  爬取京东商品数据爬虫的主程序
================================================================================
"""

import json
import logging
import re
import sys
import pymysql
import requests
from bs4 import BeautifulSoup
from scrapy import Request, Spider
from scrapy.utils.project import get_project_settings
from ..items import ProductItem, CommentItem


class JingDongSpider(Spider):
    name = "JingDong"                                                          # Scrapy Name
    allowed_domains = ["jd.com"]                                               # 作用域

    settings = get_project_settings()                                          # 实例化
    base_url = settings["BASE_URL"]                                            # 查询商品页 url
    product_url = settings["PRODUCT_URL"]                                      # 商品详情页 url
    price_url = settings["PRICE_URL"]                                          # 商品价格 url
    comment_url = settings["COMMENT_URL"]                                      # 用户对商品评论接口 url
    max_page = settings["MAX_PAGE"]                                            # 获取最大页码
    headers = settings["DEFAULT_REQUEST_HEADERS"]                              # 访问 header
    cookie = settings["USER_COOKIE"]                                           # cookie
    meta = settings["USER_META"]                                               # 匹配数据设置

    # 使用搜索词获取搜索页面结果
    def start_requests(self):                                                  # 商品 ID：sku_id
        for keyword in self.settings["KEYWORD_LIST"]:                          # 遍历所有关键词
            compare = CompareFile()
            sku_id_list = compare.compare()
            logging.info(f"获取的商品 ID 为：======> \n\t{sku_id_list}")      # 记录所有的 sku-id Logs
            print(f"总共获取商品的 ID 数目为：{len(sku_id_list)}")

            for sku_id in sku_id_list:                                         # 遍历每个 sku-id GetData
                url = self.product_url + sku_id + ".html"                      # 拼接 sku-id 得到访问 url
                # 访问商品详情页：dont_filter = True  不去重
                response = Request(url=url, callback=self.parse, dont_filter=True, meta=self.meta,
                                   headers=self.headers, cookies=self.cookie)
                yield response                                                 # 返回响应数据

    # 解析商品详情页响应数据
    def parse(self, response, **kwargs):
        store = response.xpath("//div[@class='item']/div[@class='name']/a/text()")       # 店铺名称
        brand = response.xpath("//div[@class='p-parameter']/ul[1]/li[1]/a/text()")       # 品牌
        description = response.xpath("//div[@class='p-parameter']/ul[2]/li/text()")      # 商品详情
        url = response.url                                                     # 商品链接
        sku_id = url.split("/")[-1].split(".")[0]                              # 商品 id

        item_data = ProductItem()                                              # 实例化商品描述和评价数据
        item_data["url"] = url                                                 # 商品详情页链接
        item_data["sku_id"] = sku_id                                           # 商品 ID
        item_data["store"] = "".join(store.extract())                          # 店铺名称
        item_data["brand"] = "".join(brand.extract())                          # 品牌
        item_data["description"] = ",".join(description.extract())             # 商品详细参数介绍

        print(f"正在获取商品 {sku_id} 的基本信息 ......")
        logging.info(f"\n商品  {sku_id} 的基本信息为：======> \n{item_data} ......")     # 记录日志

        # 访问价格相关接口，获取商品价格数据
        price_response = Request(url=self.price_url + sku_id, callback=self.parse_price,
                                 meta={"item": item_data})
        yield price_response

    # 解析响应的商品价格数据
    def parse_price(self, response):
        item_data = response.meta["item"]                                      # 取出上个方法封装的数据
        try:
            response_json = json.loads(response.text)                          # 解析获取的数据
        except json.decoder.JSONDecodeError:
            print(f"获取商品 {item_data['sku_id']} 价格失败，退出程序 ......")
            logging.info(f"获取商品 {item_data['sku_id']} 价格失败，退出程序 ......")
            sys.exit()

        logging.info(f"商品 {item_data['sku_id']} 响应的价格信息为： ======> \n\t{response_json}")
        price_info = response_json["price"]                                    # 获取商品价格相关的数据
        item_data["product_price"] = price_info["p"]                           # 商品价格
        try:
            fans_price = price_info["sfp"]                                     # 商品粉丝价格
        except KeyError:
            item_data["fans_price"] = ""
        else:
            item_data["fans_price"] = fans_price
        item_data["guide_price"] = price_info["op"]                            # 商品指导价
        item_data["original_price"] = price_info["m"]                          # 商品原价

        print(f"已经获取商品 {item_data['sku_id']} 的价格信息 ......")
        logging.info(f"\n商品 {item_data['sku_id']} 的价格信息为：======> \n\t{price_info} ......")

        comment_url = self.comment_url.format(item_data["sku_id"], 0)          # 拼接商品评论接口 url
        # 访问商品评价数据接口，获取商品评价数据
        comment_response = Request(url=comment_url, callback=self.parse_comment, meta={"item": item_data},
                                   headers=self.headers, cookies=self.cookie)
        yield comment_response

    # 解析响应的商品评价数据
    def parse_comment(self, response):
        item_data = response.meta["item"]
        response_json = json.loads(re.search("\((.*)\);", response.text).groups()[0])
        logging.info(f"商品 {item_data['sku_id']} 响应的评价信息为： ======> \n\t{response_json}")
        product_comment_summary = response_json["productCommentSummary"]

        # 全部评价数量.
        item_data["comment_count_list"] = [product_comment_summary["score1Count"],       # 1 星人数
                                           product_comment_summary["score2Count"],       # 2 星人数
                                           product_comment_summary["score3Count"],       # 3 星人数
                                           product_comment_summary["score4Count"],       # 4 星人数
                                           product_comment_summary["score5Count"]]       # 5 星人数
        item_data["favorable_rate"] = product_comment_summary["goodRate"]                # 好评率
        item_data["show_picture_count"] = product_comment_summary["showCountStr"]        # 晒图数量
        item_data["show_video_count"] = product_comment_summary["videoCountStr"]         # 视频晒单数量
        item_data["add_comment_count"] = product_comment_summary["afterCountStr"]        # 追评数量
        item_data["better_comment_count"] = product_comment_summary["goodCountStr"]      # 好评数量
        item_data["general_comment_count"] = product_comment_summary["generalCountStr"]  # 中评数量
        item_data["bed_comment_count"] = product_comment_summary["poorCountStr"]         # 差评数量

        hot_comment_list = response_json["hotCommentTagStatistics"]            # 热门评价数据
        comment_target_list = [["name", "count",  "type"]]                     # 评价标签
        for hot_comment in hot_comment_list:                                   # 标签类型、标签人数、标签类型
            comment_target_list.append([hot_comment["name"], hot_comment["count"], hot_comment["type"]])
        item_data["comment_target_list"] = comment_target_list                 # 评价标签赋值

        print(f"商品 {item_data['sku_id']} 的基本数据爬取结束，即将爬取该商品的评价信息 ......")
        logging.info(f"\n 商品 {response.url} 的相关信息为 ======> \n\t{item_data}")            # 打印日志
        yield item_data                                                        # 返回商品描述和评价数据

        max_page = response_json["maxPage"]                                    # 获取爬取评论页数
        print(f"商品 {item_data['sku_id']} 的评论共有 {max_page} 页 ......")
        logging.info(f"\n商品 {item_data['sku_id']} 的评论共有 {max_page} 页 ......")

        for page in range(max_page):                                           # 遍历获取所有页码的评论数据
            comment_url = self.comment_url.format(item_data["sku_id"], page)   # 凭借用户评论访问接口 url
            meta = {"sku_id": item_data["sku_id"], "page": page}
            # 访问用户评论接口，获取用户评论数据
            comment_response = Request(url=comment_url, callback=self.parse_user_comment, meta=meta)
            yield comment_response

    # 获取用户详细评价信息
    def parse_user_comment(self, response):
        # 使用正则匹配获取返回数据
        response_json = json.loads(re.search("\((.*)\);", response.text).groups()[0])
        sku_id = response_json["productCommentSummary"]["skuId"]               # 商品 ID
        logging.info(f"商品 {'sku_id'} 响应的用户详细评价信息为： ======> \n\t{response_json}")
        comment_list = response_json["comments"]                               # 评论列表

        for comment in comment_list:
            comment_item_data = CommentItem()                                  # 实例化用户对商品的评论实体类
            comment_item_data["sku_id"] = sku_id                               # 商品 ID
            comment_item_data["user_id"] = comment["id"]                       # 用户 ID
            comment_item_data["user_guid"] = comment["guid"]                   # 用户 GUID
            comment_item_data["user_name"] = comment["nickname"]               # 用户名字
            comment_item_data["user_head_url"] = comment["userImageUrl"]       # 用户头像 url
            comment_item_data["user_level"] = comment["plusAvailable"]         # 用户等级（201：PLUS会员)
            comment_item_data["score"] = comment["score"]                      # 用户评分
            comment_item_data["buy_time"] = comment["referenceTime"]           # 购买时间
            comment_item_data["comment_time"] = comment["creationTime"]        # 留言时间
            comment_item_data["item_description"] = [comment["productColor"], comment["productSize"]]  # 商品描述：颜色、尺寸
            comment_item_data["content"] = comment["content"]                  # 评论内容

            try:
                imagine_count = comment["imageCount"]                          # 评论中是否含有图片
            except KeyError:
                comment_item_data["imagine_count"] = 0                         # 评论中图片数量为 0
                comment_item_data["imagine_info_list"] = [["title", "url"]]    # 图片信息为空
            else:
                comment_item_data["imagine_count"] = imagine_count             # 图片数量
                imagine_info_list = [["title", "url"]]                         # 图片标题和图片 url
                for image_info in comment["images"]:                           # 遍历添加图片的标题和 url
                    imagine_info_list.append([image_info["imgTitle"], image_info["imgUrl"]])
                comment_item_data["imagine_info_list"] = imagine_info_list     # 图片信息
            finally:
                logging.info(f"\n图片数量：{str(comment_item_data['imagine_count'])}")

            try:
                comment_video_list = comment["videos"]                         # 评论中是否含有视频
            except KeyError:                                                   # 评论中不含有视频
                comment_item_data["video_info_list"] = [["title", "height", "width", "length", "url"]]
                comment_item_data["video_count"] = 0                           # 评论中视频数量为 0
            else:                                                              # 评论中含有视频
                video_info_list = [["title", "height", "width", "length", "url"]]
                for video_info in comment_video_list:                          # 遍历视频信息
                    title = video_info["videoTitle"]                           # 视频标题
                    height = video_info["videoHeight"]                         # 视频高度（像素）
                    width = video_info["videoWidth"]                           # 视频宽度（像素）
                    length = video_info["videoLength"]                         # 视频时长（秒：s）
                    url = video_info["remark"]                                 # 视频存放 url
                    video_info_list.append([title, height, width, length, url])
                comment_item_data["video_info_list"] = video_info_list         # 视频信息
                comment_item_data["video_count"] = len(video_info_list)        # 视频数量
            finally:                                                           # 写入日志
                logging.info(f"\n视频数量：{str(comment_item_data['video_count'])}")
            comment_item_data["like_count"] = comment["usefulVoteCount"]       # 点赞数
            comment_item_data["reply_count"] = comment["replyCount2"]          # 回复数

            try:
                after_content = comment["afterUserComment"]["content"]         # 是否含有追评
            except KeyError:
                comment_item_data["add_comment_content"] = ""                  # 不含有追评
            else:
                comment_item_data["add_comment_content"] = after_content       # 追评内容

            logging.info(f"\n 用户{comment['nickname']} 的评论信息为： ======> \n\t{comment_item_data}")
            yield comment_item_data                                            # 返回用户详细评价信息数据
        print(f"已经获取商品ID：{response.meta['sku_id']} 的第 {response.meta['page']} 页的评论信息......")


# 获取商品的 sku-id 数据
class GetItemList:
    def __init__(self, url, keyword, headers, max_page):                       # 初始化呢相关参数
        self.url = url                                                         # 查询的基本 url
        self.key_word = keyword                                                # 需要查询的关键词
        self.headers = headers                                                 # headers
        self.max_page = max_page                                               # 获取最大页码

    # 获取页面中的所有商品 ID：data-sku-id
    def query(self, page):
        header = {"user-agent": self.headers["User-Agent"]}
        data = {"keyword": self.key_word, "psort": "3", "page": str(page)}     # 请求携带的数据
        response = requests.get(url=self.url, params=data, headers=header)     # 响应数据
        soup = BeautifulSoup(response.text, "lxml")                            # 实例化 BeautifulSoup
        data_sku_list = soup.select("div[id='J_goodsList'] li[data-sku]")      # 获取所有的 sku-id

        sku_id_list = []                                                       # 存储 sku-id 列表
        for sku in data_sku_list:                                              # 遍历获取每个 sku-id
            sku_id = sku.attrs["data-sku"]                                     # 获取 sku-id 的值
            sku_id_list.append(sku_id)                                         # 添加入列表
        return sku_id_list                                                     # 返回数据

    def get_all_item(self):                                                    # 获取所有页码的数据
        sku_id_list = []                                                       # 存储 sku-id 列表
        for page in range(1, self.max_page + 1):                               # 获取每页数据
            items = self.query(page=page)                                      # 调用查询接口，获取每页的商品 sku-id
            for item in items:                                                 # 遍历每页的 sku-id
                sku_id_list.append(item)                                       # 将 sku-id 添加入列表
                logging.info(f"\n第 {page} 页的商品 ID 为：======> \n\t{item} ......")     # 记录日志
            print(f"获取第 {page} 页的商品 ID 结束 ......")
        sku_id_list = list(set(sku_id_list))                                   # 去重操作
        return sku_id_list


class CompareFile:
    def __init__(self):
        self.path = "./sku-id.csv"
        self.host = "localhost"
        self.port = 3306
        self.user = "root"
        self.pass_word = "111111"
        self.data_base = "test"

    def file_reader(self):
        data_list = []
        with open(file=self.path, mode="r", encoding="utf-8") as f:
            for line in f:
                line_string = line.strip("\n").split(",")
                data_list.append(line_string[0])
        return data_list

    def mysql_reader(self):
        connect = pymysql.connect(host=self.host, port=self.port, user=self.user,
                                  password=self.pass_word, db=self.data_base, )

        cursor = connect.cursor()
        sql = "select sku_id from ods_jingdong_product"
        cursor.execute(query=sql)
        query_result = cursor.fetchall()
        cursor.close()
        connect.close()

        data_list = []
        for q in query_result:
            data_list.append(q[0])
        return data_list

    def compare(self):
        mysql_data_list = self.mysql_reader()
        file_data_list = self.file_reader()
        result = []
        for file_data in file_data_list:
            if file_data not in mysql_data_list:
                result.append(file_data)
        return result
