### `1.` 安装  `Python`，支持 `Python 3.12+`


### `2.` 安装  `Python`  相关第三方库，命令如下：

```shell
    pip install -r requirements.txt
```


### `3.` 使用连接工具，连接  `Mysql`  创建数据库和表：

```mysql
    -- 创建数据库
    -- drop database if exists test;
    -- create database if not exists test default charset = "utf8mb4";
    -- use test;
    
    -- 创建表
    drop table if exists ods_jav_ranking;
    create table if not exists ods_jav_ranking
    (
        id                     int(16)        primary key  auto_increment          comment '自增主键',
        code                   varchar(64)    not null  default '000'              comment '视频番号',
        url                    varchar(512)   not null  default ''                 comment '视频地址',
        description            varchar(2048)  not null  default '未知'             comment '视频描述',
        station_ranking        int(8)         not null  default 0                  comment '全站排名',
        type_ranking           json                                                comment '不同类型排名',
        score                  int(8)         not null  default 0                  comment '评分',
        actor                  varchar(128)    not null  default '未知'             comment '演员',
        distributor            varchar(64)    not null  default '未知'             comment '发行商',
        director               varchar(64)    not null  default '未知'             comment '导演',
        release_date           date           not null  default '1970-01-01'       comment '发布日期',
        length                 int(8)         not null  default 0                  comment '视频长度',
        label                  varchar(512)   not null  default '未知'             comment '视频标签',
        cover_url              varchar(1024)  not null  default ''                 comment '封面图片 URL',
        thumbnail              json                                                comment '缩略图',
        magnet                 json                                                comment '视频磁力',
        comment                json                                                comment '评论',
        create_time            timestamp      not null  default current_timestamp  comment '创建时间',
        update_time            timestamp      not null  default current_timestamp on update current_timestamp comment '更新时间'
    ) engine = InnoDB default charset = "utf8mb4" comment '排行榜';
```


### `4.` 修改配置文件：
主要配置文件在 `settings.py`中：

```yaml
112-116 行:

    # Mysql 配置
    MYSQL_HOST = '127.0.0.1'
    MYSQL_PORT = 3306
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '111111'
    MYSQL_DB_NAME = 'test'
    MYSQL_CONNECT_CHARSET = 'utf8'
```


### `5.` 运行爬虫：
```bash
    # 首先切换到项目路径下：    
    cd Spider/JavRanking/
     
    # 然后： 
    scrapy crawl rank-info
```
