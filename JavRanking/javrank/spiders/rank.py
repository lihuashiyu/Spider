#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
====================================================================================================
    ProjectName    ：  crawler
    FileName       ：  rank
    CreateTime     ：  2026-10-22 20:00:52
    Author         ：  lihuashiyu
    Email          ：  lihuashiyu@github.com
    PythonCompiler ：  3.12.10
    IDE            ：  PyCharm 2024.3.6
    Version        ：  1.0
    Description    ：  文件描述
====================================================================================================
"""

from re import compile

from urllib.parse import urljoin
from scrapy import Selector, Spider, Request
from scrapy.http.response import Response
from scrapy.selector import SelectorList
from scrapy.utils.project import get_project_settings

from ..utils import logger
from ..items import TypeRanking, ThumbnailPictureUrl, VideoMagnetUrl, VideoInfoItem, VideoCommentItem, Actor


# 排行榜爬虫
class RankInfoSpider(Spider):
    name = "rank-info"                                               # 爬虫名称
    allowed_domains = ["javranking.cc"]                              # 允许的域名，多个用逗号分隔
    start_urls = ["https://javranking.cc/zh-hans/rankings"]          # 起始 url，多个用逗号分隔
    
    settings = get_project_settings()                                # 实例化设置
    meta = settings.get("USER_META")                                 # 匹配数据设置
    headers = settings.get("DEFAULT_REQUEST_HEADERS")                # 请求头
    
    video_dict = {}                                                  # 视频编号：视频 url
    
    # 解析首页
    def parse(self, response: Response):
        #
        rank_type_dict = PageParser.get_all_rank_type(html=response.text)
        # rank_type_dict = { 'DMM 本周热销榜': 'https://javranking.cc/zh-hans/rankings/dmm-weekly/' }
        for rank_type, rank_url in rank_type_dict.items():
            response = Request(url=rank_url, callback=self.parse_rank_page, dont_filter=True,
                               meta=self.meta, headers=self.headers)
            yield response                                           # 返回响应数据
            
    # 解析排行榜页面
    def parse_rank_page(self, response: Response):
        max_page = PageParser.get_max_page(html=response.text)       # 获取最大页码
        
        url = urljoin(response.url, f"?page={max_page}")             # 拼接最大页码的 url
        response = Request(url=url, callback=self.parse_video_code, dont_filter=True,
                           meta=self.meta, headers=self.headers)
        yield response                                               # 返回响应数据
        
    # 解析视频编号页面
    def parse_video_code(self, response: Response):
        base_url = f"https://{self.allowed_domains[0]}"              # 拼接基础 url
        video_url_dict =  PageParser.get_video_code(html=response.text, base_url=base_url)
        logger.info(f"{response.url} 共获取到 {len(video_url_dict)} 个视频")
        
        # 遍历视频编号和视频 url
        for video_code, video_url in video_url_dict.items():
            response = Request(url=video_url, callback=self.parse_video_info, dont_filter=True,
                               meta=self.meta, headers=self.headers)
            yield response                                           # 返回响应数据
        
    # 解析视频信息页面
    def parse_video_info(self, response: Response):
        # 获取视频信息
        video_info = PageParser.get_video_info(html=response.text, url=response.url)
        yield video_info


# 视频信息爬虫
class VideoInfoSpider(Spider):
    name = "video-info"                                              # 爬虫名称
    allowed_domains = ["javranking.cc"]                              # 允许的域名，多个用逗号分隔
    start_urls = ["https://javranking.cc/"]                          # 爬取的基本 url
    
    settings = get_project_settings()                                # 实例化设置
    meta = settings.get("USER_META")                                 # 匹配数据设置
    headers = settings.get("DEFAULT_REQUEST_HEADERS")                # 请求头
    max_page_id = settings.get(name="MAX_PAGE", default=15927)       # 最大页码
    
    def parse(self, response: Response):
        for page_id in range(1, self.max_page_id + 1):
            url = f"{self.start_urls[0]}/zh-hans/videos/{page_id}/"  # 拼接分页 url
            try:
                response = Request(url=url, callback=self.parse_video_info, dont_filter=True,
                                   meta=self.meta, headers=self.headers)
                yield response
            except Exception as e:
                logger.error(f"获取 {url} 的视频信息页面失败 ......")
            
    # 解析视频信息页面
    def parse_video_info(self, response: Response):
        # 获取视频信息
        video_info = PageParser.get_video_info(html=response.text, url=response.url)
        logger.info(f"获取 {response.url} 的视频信息 ......")
        yield video_info
    

# 解析类
class PageParser:
    RANK_PATTERN = compile(r"/rankings/([^/?#]+)/?$")                # 排行榜详情页链接特征
    RANK_SELECTOR = ".ranking-grid .ranking-card__cover"             # 排行榜卡片链接选择器
    PAGE_SELECTOR = ".pagination a, .pagination button, .pagination [data-page]"
    PAGE_PATTERN = compile(r"[?&]page=(\d+)")                        # 分页 url 中的页码特征
    
    VIDEO_INFO = "main section div"
    VIDEO_CODE_SELECTOR = "main section ol li article a"             # 视频编号选择器
    VIDEO_DESCRIPTION_SELECTOR = f"{VIDEO_INFO}[class='video-hero']" # 视频信息选择器
    VIDEO_PICTURE_SELECTOR = f"{VIDEO_INFO}[id='preview-gallery']"   # 视频图片选择器
    VIDEO_MAGNET_SELECTOR = f"{VIDEO_INFO} ul li[class='magnet-item']" # 视频磁力链接选择器
    VIDEO_COMMENT_SELECTOR = f"{VIDEO_INFO} ol li"                   # 视频评论选择器
    
    # 获取页面中全部排行榜的名称和 url
    @staticmethod
    def get_all_rank_type(html: str) -> dict[str, str]:
        host = RankInfoSpider.allowed_domains[0]                     # 排行榜所在域名
        base_url = f"https://{host}"                                 # 拼接基础 url
        covers = Selector(text=html).css(PageParser.RANK_SELECTOR)   # 全部排行榜卡片
        
        rank_type_dict: dict[str, str] = {}                          # 排行榜名称：排行榜 url
        for cover in covers:
            title = cover.attrib.get("title", "").strip()            # 排行榜名称
            href = cover.attrib.get("href", "").strip()              # 排行榜相对链接
            
            if not title or not PageParser.RANK_PATTERN.search(href):
                continue                                             # 跳过无效的排行榜
            
            rank_type_dict[title] = urljoin(base_url, href)          # 拼接完整排行榜 url
        
        logger.info(f"共获取到 {len(rank_type_dict)} 个排行榜， {rank_type_dict}")
        return rank_type_dict
    
    # 获取排行榜页面分页组件中的最大页码
    @staticmethod
    def get_max_page(html: str) -> int:
        selector = Selector(text=html)                               # 实例化 Selector
        items = selector.css(PageParser.PAGE_SELECTOR)               # 分页组件中的条目
        if not items:
            items = selector.css("a[href*='page=']")                 # 兜底：页面中的页码链接
        
        pages: list[int] = []                                        # 收集所有出现的页码
        for item in items:
            page = item.attrib.get("data-page", "").strip()          # data-page 属性中的页码
            href = item.attrib.get("href", "").strip()               # 分页 url 中的页码
            text = item.xpath("string(.)").get(default="").strip()   # 分页文本中的页码
            
            # 提取 href 中的页码
            pages.extend(int(value) for value in PageParser.PAGE_PATTERN.findall(href))
            if page.isdigit():                                       # 判断 page 是否为数字
                pages.append(int(page))
                
            if text.isdigit():                                       # 判断 text 是否为数字
                pages.append(int(text))
        
        max_page = max(pages, default=1)                             # 获取最大页码
        logger.info(f"排行榜 共有 {max_page} 页 ......")
        return max_page                                              # 返回最大页码
        
    # 获取排行榜页面中全部视频的编号和 url
    @staticmethod
    def get_video_code(html: str, base_url: str) -> dict[str, str]:
        # 获取视频编号和视频 url
        selectors = Selector(text=html).css(query=PageParser.VIDEO_CODE_SELECTOR)
        
        video_url_dict: dict[str, str] = {}                          # 视频编号：视频 url
        for selector in selectors:
            video_uri = selector.attrib.get("href", "").strip()      # 视频相对链接
            video_code = selector.attrib.get("aria-label", "").split(":")[0].strip() # 视频编号
            
            if video_uri and video_code:                             # 判断视频编号和视频 url 是否为空
                video_url = urljoin(base_url, video_uri)             # 拼接完整视频 url
                video_url_dict[video_code] = video_url               # 添加视频编号和视频 url 到字典中
        
        return video_url_dict
        
    # 获取视频信息
    @staticmethod
    def get_video_info(html: str, url: str) -> VideoInfoItem:
        # 获取视频描述信息
        description_selectors = Selector(text=html).css(query=PageParser.VIDEO_DESCRIPTION_SELECTOR)
        video_info = PageParser.__get_video_description(selector_list=description_selectors)
        
        # 获取视频图片信息
        video_info.url = url
        
        # 获取视频图片信息
        picture_selectors = Selector(text=html).css(query=PageParser.VIDEO_PICTURE_SELECTOR)
        video_info.thumbnail = PageParser.__get_video_picture(selector_list=picture_selectors)
        
        # 获取视频磁力链接信息
        magnet_selectors = Selector(text=html).css(query=PageParser.VIDEO_MAGNET_SELECTOR)
        video_info.magnet = PageParser.__get_video_magnet(selector_list=magnet_selectors)
        
        # 获取视频评论信息
        comment_selectors = Selector(text=html).css(query=PageParser.VIDEO_COMMENT_SELECTOR)
        video_info.comment = PageParser.__get_video_comment(selector_list=comment_selectors)
        
        return video_info
    
    # 获取视频描述信息
    @staticmethod
    def __get_video_description(selector_list: SelectorList) -> VideoInfoItem:
        video_info = VideoInfoItem()                                 # 创建视频信息对象
        
        # 获取封面图片 url
        cover_picture_url = selector_list.css(query="div[class='cover-art video-cover'] img").attrib.get("src", "")
        video_info.cover_url = cover_picture_url.strip()             # 设置封面图片 url
        
        type_ranking_list = []                                       # 当前类排名列表
        for type_ranking_selector in selector_list.css(query="aside ul li"):
            type_ranking = TypeRanking()                             # 创建类型排名对象
            type_ranking.type = type_ranking_selector.css(query="a span::text").get(default="").strip()
            
            ranking = type_ranking_selector.css(query="a strong::text").get(default="#0").split("#")[-1].strip()
            type_ranking.ranking = int(ranking) if ranking.isdigit() else None
            type_ranking_list.append(type_ranking)                  # 添加类型排名对象到列表中
        video_info.type_ranking = type_ranking_list                 # 设置类型排名列表
        
        # 获取视频摘要信息
        video_summary_selectors = selector_list.css(query="div div[class='video-summary']")
        video_info.code = video_summary_selectors.css(query="div p[class='video-code']::text").get(default="").strip()
        video_info.description = video_summary_selectors.css(query="h1[lang]::text").get(default="").strip()
        
        # 获取视频演员信息
        actor_selector_selectors = video_summary_selectors.css(query="p[class='video-mobile-cast']")
        actor_list = []                                              # 演员列表
        for actor_selector in actor_selector_selectors:
            actor = Actor()                                          # 创建演员对象
            actor.name = actor_selector.css(query="a::text").get(default="").strip()
            actor.gender = actor_selector.css(query="span::attr(title)").get(default="").strip()
            actor_list.append(actor)                                 # 添加演员对象到列表中
        video_info.actor = actor_list                                # 设置演员列表
        
        # 获取视频排名信息
        station_ranking_selector = "div a[class='ranking-stats__item ranking-stats__item--rank'] strong::text"
        station_ranking = video_summary_selectors.css(query=station_ranking_selector).get(default="#0")
        video_info.station_ranking = int(station_ranking.split("#")[-1].strip())
        
        # 获取视频评分信息
        score_selector = "div span[class='ranking-stats__item ranking-stats__item--score'] strong::text"
        score = video_summary_selectors.css(query=score_selector).get(default="0").strip()
        video_info.score = int(score.replace(",", ""))
        
        # 获取视频标签信息
        video_label = video_summary_selectors.css(query="p[class='video-mobile-categories'] a[class='entity-link']::text").getall()
        video_info.label = "@".join(video_label)
        
        # 获取视频时长信息
        duration = video_summary_selectors.css(query="p[class='video-tablet-date-duration']::text").get().split("·")
        if len(duration) > 1:
            release_date = duration[0].strip().replace("年", "-").replace("月", "-").replace("日", "").strip()
            video_info.release_date = release_date if release_date else "2029-12-31"
            
            video_info.length = duration[1].strip().split(" ")[0].strip()
        
        # 获取视频发行信息
        distributor_selector = "dl div[class='video-tablet-facts__row video-tablet-facts__row--maker'] dd a::text"
        video_info.distributor = video_summary_selectors.css(query=distributor_selector).get(default="未知").strip()
        
        # 获取视频导演信息
        director_selector = "dl div[class='video-tablet-facts__row video-tablet-facts__row--director'] dd a::text"
        video_info.director = video_summary_selectors.css(query=director_selector).get(default="未知").strip()
        
        return video_info
            
    # 获取视频图片信息
    @staticmethod
    def __get_video_picture(selector_list: SelectorList) -> list[ThumbnailPictureUrl]:
        # 获取缩略图 url 列表
        thumbnail_selector = "div a[class='preview-gallery__trigger']::attr(href)"
        thumbnail_url_list = selector_list.css(query=thumbnail_selector).getall()
        
        # 创建缩略图对象列表
        thumbnail_picture_url_list = []                              # 缩略图对象列表
        for index, thumbnail_url in enumerate(thumbnail_url_list):
            thumbnail_picture_url = ThumbnailPictureUrl()            # 创建缩略图对象
            thumbnail_picture_url.id = index + 1                     # 设置缩略图 id
            thumbnail_picture_url.url = thumbnail_url.strip()        # 设置缩略图 url
            thumbnail_picture_url_list.append(thumbnail_picture_url)
        
        logger.info(f"共获取到 {len(thumbnail_picture_url_list)} 条缩略图")
        return thumbnail_picture_url_list
    
    # 获取视频磁力链接信息
    @staticmethod
    def __get_video_magnet(selector_list: SelectorList) -> list[VideoMagnetUrl]:
        magnet_list = []                                             # 磁力链接对象列表
        for index, magnet_selector in enumerate(selector_list):
            magnet = VideoMagnetUrl()                                # 创建磁力链接对象
            magnet.id = index + 1                                    # 设置磁力链接 id
            
            # 获取磁力链接名称和 url
            item_header = magnet_selector.css(query="div[class='magnet-item__header']")
            magnet.name = item_header.css(query="a::text").get(default="").strip()
            magnet.url = item_header.css("a::attr(href)").get(default="").strip()
            
            # 获取磁力链接大小
            size = magnet_selector.css(query="span[class='magnet-tag magnet-tag--size']::text").get(default="0GB")
            magnet.size = size.strip()
            
            # 视频清晰度和字幕
            other_list = magnet_selector.css(query="span[class='magnet-tag']::text").getall()
            if len(other_list) == 1:
                magnet.clarity = other_list[0].strip()               # 设置清晰度
            elif len(other_list) > 1:
                magnet.clarity = other_list[0].strip()               # 设置清晰度
                magnet.is_subtitle = 1                               # 设置字幕标志
            
            # 获取 picpak 链接地址
            magnet.picpak_url = magnet_selector.css(query="div[class='magnet-item__actions'] a::attr(href)").get(default="")
            magnet_list.append(magnet)
            
        logger.info(f"共获取到 {len(magnet_list)} 条磁力链接")
        return magnet_list
    
    # 获取视频评论信息
    @staticmethod
    def __get_video_comment(selector_list: SelectorList) -> list[VideoCommentItem]:
        video_comment_list = []                                      # 评论对象列表
        for index, selector in enumerate(selector_list):
            video_comment = VideoCommentItem()                       # 创建评论对象
            video_comment.id = index + 1                             # 设置评论 id
            
            # 获取评论内容
            video_comment.comment = selector.css("p::text").get(default="")
            if video_comment.comment:
                user_info = selector.css("div")                      # 获取用户信息
                if user_info:
                    # 获取用户信息
                    user = user_info.css(query="span[class='review-author']::text").get(default="")
                    video_comment.user = user.strip()
                    
                    # 获取评论时间
                    date = user_info.css(query="time::text").get(default="1970-01-01").strip()
                    video_comment.date = date.replace("年", "-").replace("月", "-").replace("日", "").strip()
                    
                    # 获取评论评分
                    score = user_info.css(query="span[class='review-rating']::text").get(default="0.0").strip()
                    video_comment.score = float(score)
                    
                    # 获取评论点赞数
                    like_count = user_info.css(query="span span::text").get(default="0").strip()
                    video_comment.like = int(like_count)
                    
                    video_comment_list.append(video_comment)
        
        logger.info(f"共获取到 {len(video_comment_list)} 条评论")
        return video_comment_list
