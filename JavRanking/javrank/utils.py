#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
====================================================================================================
    ProjectName    ：  crawler  
    FileName       ：  utils
    CreateTime     ：  2026-10-22 20:00:52 
    Author         ：  lihuashiyu 
    Email          ：  lihuashiyu@github.com 
    PythonCompiler ：  3.12.10 
    IDE            ：  PyCharm 2024.3.6  
    Version        ：  1.0 
    Description    ：  文件描述 
====================================================================================================
"""

from sys import stdout
from pathlib import Path
from typing import Optional, Any
from json import dumps

from dataclasses import is_dataclass, asdict
from loguru import logger as logging
from contextvars import ContextVar
from pymysql.connections import Connection
from pymysql.cursors import DictCursor
from scrapy.utils.project import get_project_settings


# ================= 彩色日志格式器 (仅用于控制台) =================
class ColorLogFormat:
    def __init__(self):
        conf = get_project_settings()                                # 实例化
        
        self.log_format = conf.get("LOGURU_FORMAT")                  # 日志格式
        self.console_enable = conf.get("CONSOLE_ENABLE")             # 控制台是否启用
        self.console_level = conf.get("CONSOLE_LEVEL")               # 控制台级别
        self.file_enable = conf.get("FILE_ENABLE")                   # 文件是否启用
        self.file_level = conf.get("FILE_LEVEL")                     # 文件级别
        self.log_name = conf.get("FILE_PATH")                        # 日志文件名
        self.file_rotation = conf.get("FILE_ROTATION")               # 日志文件轮转
        self.file_retention = conf.get("FILE_RETENTION")             # 日志文件保存时长
    
    def profile(self):
        logging.remove()
        patched_logger = logging.patch(patcher=self.__inject_request_id)
        
        if self.console_enable:
            patched_logger.add(sink=stdout, level=self.console_level, format=self.log_format)
        
        if self.file_enable:
            self.__create_log_dir()
            
            patched_logger.add(sink=self.log_name, level=self.file_level, format=self.log_format,
                        rotation=self.file_rotation, retention=self.file_retention, encoding="utf-8")
        return patched_logger
        
    def __create_log_dir(self) -> None:
        path = Path(self.log_name).parent                            # 日志文件路径
        
        if path.exists() and path.is_dir():                          # 判断路径是否存在
            return
        
        path.mkdir(parents=True, exist_ok=True)                      # 创建路径
    
    @classmethod
    def __inject_request_id(cls, record: dict[str, dict[str, str]]):
        request_id = ContextVar("request_id", default="1").get()
        record["extra"]["request_id"] = request_id


logger = ColorLogFormat().profile()


class JsonEncoder():
    # 将 dataclass、列表等复合结构序列化为 JSON 字符串
    @staticmethod
    def json_dumps(value: Any) -> str:
        def _default(obj: Any) -> Any:
            if is_dataclass(obj) and not isinstance(obj, type):
                return asdict(obj)                                   # dataclass 转为字典
            return str(obj)                                          # 其他类型兜底转为字符串
        
        json_str = dumps(value if value is not None else [], ensure_ascii=False, default=_default)
        return json_str
        
# Mysql 连接
class MysqlClient:
    # 初始化数据
    def __init__(self, conf : dict[str, Any]) -> None:
        self.host = conf.get("HOST", "localhost")                    # Mysql IP 地址
        self.port = conf.get("PORT", 3306)                           # Mysql 端口
        self.user = conf.get("USER", "root")                         # Mysql 用户名
        self.password = conf.get("PASSWORD", "")                     # Mysql 密码
        self.database = conf.get("DATABASE", "test")                 # Mysql 数据库名
        self.charset = conf.get("CHARSET", "utf8mb4")                # Mysql 字符集
        
        self.connection: Optional[Connection] = None                 # Mysql 连接
        
    # 初始化数据
    def __enter__(self):
        if self.connection is None:                                  # 如果连接为空
            self.connect()                                           # 连接数据库
        return self
    
    # 关闭数据库连接
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self.connection is not None:
            self.close()                                             # 关闭数据库连接
        
        if exc_type:
            logger.warning(f"type = {exc_type}, value = {exc_val}")  # 记录异常信息
        
        return False                                                 # 不吞异常，交由调用方处理
        
    # 连接数据库
    def connect(self) -> None:
        try:
            # 创建连接
            self.connection = Connection(host=self.host, port=self.port, user=self.user,
                                         password=self.password, db=self.database, charset=self.charset)
            
            logger.info(f"=============== 连接到 {self.host} ===============")
        except Exception as e:
            logger.error(f"=============== mysql 连接异常：{e} ===============")
            logger.error(f"error = {e}")
            
    # 执行 sql
    def execute_sql(self, sql: str, data_tuple: Optional[tuple] = None) -> Any:
        if self.connection is None or not self.connection.open:      # 连接不存在或已断开
            self.connect()                                           # 连接数据库
        
        result_tuple = ()
        try:
            with self.connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(query=sql, args=data_tuple)            # 执行 sql
                
                # 判断是否有结果集
                if cursor.description is not None:
                    result_tuple = cursor.fetchall()                 # 获取结果集
                else:
                    result_tuple = cursor.rowcount                   # 获取受影响行数
                
                self.connection.commit()                             # 提交事务
                logger.debug(f"=============== 执行成功 ===============")
        except Exception as e:
            self.connection.rollback()                               # 回滚事务
            logger.error(f"=============== 查询异常：{e} ===============")
        finally:
            return result_tuple
            
    # 关闭数据库连接
    def close(self) -> None:
        try:
            self.connection.close()                                  # 关闭数据库连接
            logger.info(f"=============== {self.host} 的连接已关闭 ===============")
        except Exception as e:
            logger.error(f"=============== mysql 关闭异常：{e} ===============")
