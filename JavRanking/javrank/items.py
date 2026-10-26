# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class TypeRanking:
    type: Optional[str] = None                                       # 类别
    ranking: Optional[int] = None                                    # 排名


@dataclass
class Actor:
    name: Optional[str] = None                                       # 演员名称
    gender: Optional[str] = None                                     # 演员性别


@dataclass
class ThumbnailPictureUrl:
    id: Optional[int] = 0                                            # 缩略图 ID
    url: Optional[str] = ""                                          # 缩略图 URL
    

@dataclass
class VideoMagnetUrl:
    id: Optional[int] = 0                                            # 磁力链接 ID
    name: Optional[str] = None                                       # 磁力链接名称
    url: Optional[str] = None                                        # 磁力链接
    size: Optional[str] = "0GB"                                      # 磁力链接大小
    clarity: Optional[str] = "unknown"                               # 磁力链接清晰度
    is_subtitle: Optional[int] = 0                                   # 是否字幕
    picpak_url: Optional[str] = ""                                   # 磁力链接图片 URL


@dataclass
class VideoCommentItem:
    id: Optional[int] = 0                                            # 评论 ID
    user: Optional[str] = None                                       # 用户 ID
    comment: Optional[str] = ""                                      # 评论
    date: Optional[str] = "1970-01-01"                               # 评论时间
    score: Optional[float] = 0.0                                     # 评分
    like: Optional[int] = 0                                          # 赞同数量

    
@dataclass
class VideoInfoItem:
    code: Optional[str] = None                                       # 视频番号
    url: Optional[str] = None                                        # 视频地址
    description: Optional[str] = None                                # 视频描述
    station_ranking: int = 0                                         # 站点排名
    type_ranking: List[TypeRanking] = field(default_factory=list)    # 不同类型排名
    score: int = 0                                                   # 评分
    actor: List[Actor] = field(default_factory=list)                 # 演员
    distributor: str = "未知"                                        # 发行商
    director: str = "未知"                                           # 导演
    release_date: Optional[str] = "2029-12-31"                       # 发布日期，表中为 varchar(16)
    length: Optional[int] = 0                                        # 视频长度
    label: str = ""                                                  # 视频标签
    cover_url: str = ""                                              # 封面图片 URL
    thumbnail: List[ThumbnailPictureUrl] = field(default_factory=list)    # 缩略图
    magnet: List[VideoMagnetUrl] = field(default_factory=list)       # 视频磁力
    comment: List[VideoCommentItem] = field(default_factory=list)    # 评论
