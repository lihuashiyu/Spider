# Scrapy settings for javrank project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from random import random
from os.path import abspath

# ======================================== 基本配置 ======================================== #
BOT_NAME = "javrank"                                       # 项目名称，Scrapy 用此标识该项目

SPIDER_MODULES = ["javrank.spiders"]                       # Scrapy 自动查找爬虫的模块列表
NEWSPIDER_MODULE = "javrank.spiders"                       # genspider 创建新爬虫的存放模块
ADDONS = {}                                                # 自定义附加组件配置，默认留空

# ======================================== 爬虫配置 ======================================== #
ROBOTSTXT_OBEY = True                                      # 是否遵守站点的 robots.txt 协议
CONCURRENT_REQUESTS = 16                                   # 全局最大并发请求数
CONCURRENT_REQUESTS_PER_DOMAIN = 1                         # 同一域名允许的最大并发请求数
DOWNLOAD_DELAY = random() * 5                              # 下载延迟（秒），控制爬取频率
COOKIES_ENABLED = True                                     # 是否启用 Cookie，False 表示禁用
TELNETCONSOLE_ENABLED = False                              # 是否启用 Telnet 控制台，False 表示禁用

# ======================================= 中间件配置 ======================================= #、
# 用户代理，用于向目标站点标识爬虫身份
USER_AGENT = "ozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36 Edg/155.0.0.0"

# 覆盖默认的标头
DEFAULT_REQUEST_HEADERS = \
    {
        "Accept"            : "*/*",                       # 接受的数据内容
        "Accept-Encoding"   : "gzip, deflate, br, zstd",   # 接受的压缩编码
        "Connection"        : "keep-alive",                # 保持连接状态
        "cache-control"     : "max-age=0",                 # 缓存控制
        "User-Agent"        : USER_AGENT,                  # UA
        "Accept-Language"   : "zh-CN,zh;q=0.9",            # 接受语言
        "Origin"            : "https://item.jd.com",       # 网页来源
        "Referer"           : "https://search.jd.com/",    # 跳转页面
        "sec-ch-ua-platform": "Windows",                   # 操作系统
        "sec-ch-ua-mobile"  : "?0",                        # 是否移动设备
        "sec-fetch-dest"    : "document",                  # 获取目标
        "sec-fetch-mode"    : "navigate",                  # 获取模式
        "sec-fetch-site"    : "same-origin",               # 获取站点
        "sec-ch-ua"         : "' Not;A Brand';v='99', 'Microsoft Edge';v='91', 'Chromium';v='91'",
    }

#  匹配数据设置
USER_META = \
    {
        "dont_redirect": True,                             # 禁止网页重定向
        "handle_http_status_list": [301, 302]              # 对哪些异常返回进行处理
    }

# 爬虫中间件及其优先级
SPIDER_MIDDLEWARES = \
    {
        "javrank.middlewares.JavrankSpiderMiddleware": 543,
    }

# 下载器中间件及其优先级
DOWNLOADER_MIDDLEWARES = \
    {
        "javrank.middlewares.JavrankDownloaderMiddleware": 543,
    }

# 扩展组件及其优先级，值为 None 表示禁用
EXTENSIONS = \
    {
        "scrapy.extensions.telnet.TelnetConsole": None,
    }

# 数据管道及其执行顺序，数值越小越先执行
ITEM_PIPELINES = \
    {
        "javrank.pipelines.MysqlPipeline": 300,
    }

# ======================================= 限速配置 ======================================= #

AUTOTHROTTLE_ENABLED = True                                # 是否启用自动限速扩展
AUTOTHROTTLE_START_DELAY = 5                               # 初始下载延迟（秒）
AUTOTHROTTLE_MAX_DELAY = 60                                # 最大下载延迟（秒）
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0                      # 每个域名并发请求数的目标值
AUTOTHROTTLE_DEBUG = False                                 # 是否输出限速调试统计

# ======================================= 缓存配置 ======================================= #
HTTPCACHE_ENABLED = True                                   # 是否启用 HTTP 缓存
HTTPCACHE_EXPIRATION_SECS = 0                              # 缓存过期时间（秒），0 表示永不过期
HTTPCACHE_DIR = "httpcache"                                # 缓存文件存放目录
HTTPCACHE_IGNORE_HTTP_CODES = []                           # 不缓存的 HTTP 状态码列表
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"  # 缓存存储后端实现
FEED_EXPORT_ENCODING = "utf-8"                             # 导出数据的编码格式

# ======================================== 日志配置 ======================================== #
PYTHON_FILE_PATH = abspath(path=__file__)                  # 当前配置文件的绝对路径
LOG_DIR = abspath(path=f"{PYTHON_FILE_PATH}/../../logs")   # 日志所在目录
FILE_PATH = abspath(path=f"{LOG_DIR}/{BOT_NAME}.log")      # 文件日志路径
LOG_LEVEL = "INFO"                                         # 日志级别，DEBUG、INFO、WARNING、ERROR、CRITICAL
CONSOLE_ENABLE = True                                      # 是否启用控制台输出
CONSOLE_LEVEL = LOG_LEVEL                                  # 控制台日志级别
FILE_ENABLE = True                                         # 是否启用文件输出
FILE_LEVEL = LOG_LEVEL                                     # 文件日志级别
FILE_ROTATION = "7 days"                                   # 文件轮转周期
LOGURU_FORMAT = "[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>]-|-<<level>{level}</level>>-|-<magenta>task: {extra[request_id]}</magenta>-|-<cyan>{name}</cyan>: <cyan>{function}</cyan>: <cyan>{line}</cyan>-|-<level>{message}</level>"

# ======================================== Mysql 配置 ======================================== #
HOST = "127.0.0.1"                                         # 主机地址
PORT = 3306                                                # 端口号
USER = "test"                                              # 用户名
PASSWORD = "111111"                                        # 密码
DATABASE = "test"                                          # 数据库名
CHARSET = "utf8mb4"                                        # 字符集

INSERT_RANK_INFO = "insert into ods_jav_ranking (code, url, description, station_ranking, type_ranking, score, actor, distributor, director, release_date, length, label, cover_url, thumbnail, magnet, comment)" \
            "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

# ======================================== 其他配置 ======================================== #
MAX_PAGE = 15927                                           # 最大页数
