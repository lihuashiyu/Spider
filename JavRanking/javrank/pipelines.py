# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.utils.project import get_project_settings

from .utils import MysqlClient, logger, JsonEncoder
from .items import VideoInfoItem

# 将获取的数据写入到 Mysql 数据库
class MysqlPipeline:
    # 初始化数据库连接参数：数据库地址、端口号、用户名、密码、数据库名、连接字符集
    def __init__(self, mysql: MysqlClient):
        self.mysql: MysqlClient = mysql
        
    # 获取配置文件中的参数
    @classmethod
    def from_crawler(cls, crawler):                                  # 从 settings Mysql 参数
        return cls(mysql=MysqlClient(conf=crawler.settings))
        
    # 建立连接
    def open_spider(self, spider):
        self.settings = get_project_settings()                       # 实例化 settings
        
    # 写入数据
    def process_item(self, item, spider):
        if isinstance(item, VideoInfoItem):                          # 若是视频信息实体类
            sql = self.settings["INSERT_RANK_INFO"]                  # 获取 sql
            # 获取视频信息相关参数：多值字段统一序列化为 JSON 字符串
            data_tuple = (item.code,                                  item.url,
                          item.description,                           item.station_ranking,
                          JsonEncoder.json_dumps(item.type_ranking),  item.score,
                          JsonEncoder.json_dumps(item.actor),         item.distributor,
                          item.director,                              item.release_date,
                          item.length,                                item.label,
                          item.cover_url,                             JsonEncoder.json_dumps(item.thumbnail),
                          JsonEncoder.json_dumps(item.magnet),        JsonEncoder.json_dumps(item.comment))
            
            self.mysql.execute_sql(sql=sql, data_tuple=data_tuple)   # 执行 sql
        else:
            logger.warning(f"不存在此{item}")                        # 记录日志
            
        return item
    
    # 关闭连接
    def close_spider(self, spider):
        self.mysql.close()
        
