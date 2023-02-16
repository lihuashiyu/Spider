#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
================================================================================
    ProjectName   ：  Spyder
    FileName      ：  settings
    CreateTime    ：  2021-09-11 12:38:00
    Author        ：  Administrator
    Email         ：
    PythonCompiler：  3.9.5
    IDE           ：  PyCharm 2020.3.4
    Version       ：  1.0
    Description   ：  Scrapy 框架配置文件
================================================================================
"""

import datetime

# 爬虫项目名称
BOT_NAME = "GetData"

# 项目模块
SPIDER_MODULES = ["GetData.spiders"]
NEWSPIDER_MODULE = "GetData.spiders"

# 是否遵循 robots 协议
ROBOTSTXT_OBEY = False

# 配置由 Scrapy 执行的最大并发请求(默认值: 16)
CONCURRENT_REQUESTS = 16

# 为相同网站请求间隔时长(默认为0)
DOWNLOAD_DELAY = 3

# 通过在用户代理上识别你自己(和你的网站)负责爬行
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
             "Chrome/92.0.4515.107 Safari/537.36"

# 下载延迟设置只会遵循以下其中之一:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# 是否关闭 cookies (默认启用)
COOKIES_ENABLED = True

# 是否禁用 Telnet 控制台(默认启用)
# TELNETCONSOLE_ENABLED = False

# 覆盖默认的标头
DEFAULT_REQUEST_HEADERS = \
    {
        "Accept":          "*/*",                          # 接受的数据内容
        "Accept-Encoding": "gzip, deflate, br",            # 接受的压缩编码
        "Connection":      "keep-alive",                   # 保持连接状态
        "User-Agent":      USER_AGENT,                     # UA
        "Accept-Language": "zh-CN,zh;q=0.9",               # 接受语言
        "Origin":          "https://item.jd.com",          # 网页来源
        "Referer":         "https://search.jd.com/",       # 跳转页面
        "sec-ch-ua":       "' Not;A Brand';v='99', 'Microsoft Edge';v='91', 'Chromium';v='91'",
    }

#  匹配数据设置
USER_META = \
    {
        "dont_redirect": True,                             # 禁止网页重定向
        "handle_http_status_list": [301, 302]              # 对哪些异常返回进行处理
    }

# 启用或禁用爬行器中间件
# SPIDER_MIDDLEWARES = {"GetData.middlewares.GetdataSpiderMiddleware": 543, }

# 启用或禁用下载器中间件
# DOWNLOADER_MIDDLEWARES = \
#     {
#         "GetData.middlewares.GetdataDownloaderMiddleware": 543,
#         "GetData.middlewares.ProxyMiddleware": 543,
#     }

# 启用或禁用下载器中间件扩展
# EXTENSIONS = { "scrapy.extensions.telnet.TelnetConsole": None, }
# 配置项管道
ITEM_PIPELINES = \
    {
        "GetData.pipelines.WriteDataPipeline": 300,
        # "GetData.pipelines.CommentPipeline": 301,
        # 开启 Mysql 管道，把数据存到 Mysql 数据库
        "GetData.pipelines.MysqlPipeline":     302,
    }

# 启用和配置 AutoThrottle 扩展(默认禁用)
# AUTOTHROTTLE_ENABLED = True
# 初始下载延迟
# AUTOTHROTTLE_START_DELAY = 5
# 在高延迟情况下设置的最大下载延迟
# AUTOTHROTTLE_MAX_DELAY = 60
# Scrapy 应该并行发送到每个远程服务器的请求的平均数量
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# 为每次收到的响应显示节流数据
# AUTOTHROTTLE_DEBUG = False

# 启用和配置 HTTP 缓存(默认禁用)
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# HTTPERROR_ALLOWED_CODES = [403]

# 设置重复过滤器的模块
# DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# 设置调取器，scrap_redis中的调度器具备与数据库交互的功能
# SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# 配置日志级别：CRITICAL（严重错误）、ERROR（一般错误）、WARNING（警告信息）INFO（一般信息）、DEBUG（调试信息）
LOG_LEVEL = "INFO"
# 是否启用 logging（默认: True）
LOG_ENABLED = True
# 日志编码格式（默认: utf-8）
LOG_ENCODING = "utf-8"
# 是否程序内的所有 print 将会被输送到日志文件内（默认：False）
LOG_STDOUT = False
# 配置日志文件名和位置（默认: None）
time = datetime.datetime.now()
LOG_FILE = "../../Other/Log/JingDong-{}-{}-{}.log".format(time.year, time.month, time.day)

# 数据写入本地路径
PRODUCT_PATH = "../../Other/Data/product-{}-{}-{}-{}.json".format(time.month, time.day, time.hour, time.minute)
COMMENT_PATH = "../../Other/Data/comment-{}-{}-{}-{}.json".format(time.month, time.day, time.hour, time.minute)

# sqlite 配置
# SQLITE_DB_NAME = "scrapy.db"

# 搜索列表
KEYWORD_LIST = ["手机"]
# 查询的页码
MAX_PAGE = 100
# 登录后用户 cookie
USER_COOKIE = \
    {
        "shshshfpa":    "a1631343865",
        "shshshfpb":    "UrMM0c8hQ",
        "areaId":       "15",
        "ipLoc-djd":    "15-1213-3411-0",
        "unpl":         "Je",
        "__jdv":        "039",
        "pinId":        "A",
        "pin":          "%8E",
        "unick":        "%E",
        "_tp":          "AgBF",
        "_pst":         "%%8E",
        "user-key":     "68c",
        "PCSYCityID":   "CN_",
        "ceshi3.com":   "0",
        "__jdc":        "120672",
        "wlfstk_smdl":  "6pql",
        "TrackID":      "GM",
        "shshshfp":     "c",
        "__jda":        "12211.23",
        "thor":         "C92"
    }

# 代理池
PROXY_POOL = \
    [
        "http://91.90.123.115:34687",
    ]

# 查询商品页 url
BASE_URL = "https://search.jd.com/Search?"
# 商品详情页 url
PRODUCT_URL = "https://item.jd.com/"
# 商品价格接口 url
PRICE_URL = "https://item-soa.jd.com/getWareBusiness?skuId="
# PRICE_URL = "https://p.3.cn/prices/mgets?skuIds=J_"
# 用户对商品评论接口 url
COMMENT_URL = "https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98" \
              "&productId={}&score=0&sortType=6&page={}&pageSize=10&isShadowSku=0&fold=1"

# Mysql 配置
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "111111"
MYSQL_DB_NAME = "test"
MYSQL_CONNECT_CHARSET = "utf8"

# 插入 Mysql 数据库所用的 sql 语句
PRODUCT_SQL = "insert into ods_jingdong_product(sku_id, store, product_price, fans_price, " \
              "guide_price, original_price, brand, description, url, comment_count, " \
              "favorable_rate, comment_target, show_picture_count, show_video_count, " \
              "add_comment_count, better_comment_count, general_comment_count, bed_comment_count) " \
              "values(%s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"

COMMENT_SQL = "insert into ods_jingdong_comment(sku_id, user_id, user_guid, user_name, " \
              "user_head_url, user_level, score, buy_time, comment_time, item_description, " \
              "content, imagine_count, imagine_info, video_count, video_info, like_count, " \
              "reply_count, add_comment_content) " \
              "values(%s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
