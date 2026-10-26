# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from itemadapter import ItemAdapter


# 爬虫中间件
class JavrankSpiderMiddleware:
    # 由 Scrapy 调用创建实例
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()                                                    # 实例化中间件
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened) # 绑定爬虫开启信号
        return s                                                     # 返回中间件实例
    
    # 处理进入爬虫的响应
    def process_spider_input(self, response, spider):
        return None                                                  # 返回 None 表示继续处理
    
    # 处理爬虫输出的结果
    async def process_spider_output(self, response, result, spider):
        async for item_or_request in result:                         # Scrapy 2.19 要求异步迭代
            yield item_or_request                                    # 原样输出请求或数据
    
    # 处理爬虫抛出的异常
    def process_spider_exception(self, response, exception, spider):
        pass                                                         # 返回 None 表示继续传递
    
    # 处理起始请求的异步迭代器
    async def process_start(self, start):
        async for item_or_request in start:                          # 异步遍历起始请求
            yield item_or_request                                    # 原样输出请求
    
    # 爬虫开启回调
    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)        # 记录爬虫名称


# 下载器中间件
class JavrankDownloaderMiddleware:
    # 由 Scrapy 调用创建实例
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()                                                    # 实例化中间件
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)  # 绑定爬虫开启信号
        return s                                                     # 返回中间件实例
    
    # 处理每个请求
    def process_request(self, request, spider):
        return None                                                  # 返回 None 表示继续处理
    
    # 处理下载器返回的响应
    def process_response(self, request, response, spider):
        return response                                              # 原样返回响应
    
    # 处理下载异常
    def process_exception(self, request, exception, spider):
        pass                                                         # 返回 None 表示继续传递
    
    # 爬虫开启回调
    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)        # 记录爬虫名称
