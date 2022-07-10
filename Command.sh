#!/usr/bin/env bash


# 1. 项目创建
scrapy startproject Demo

# 创建 spider，首先进入 Demo 文件夹
scrapy genspider demo 'www.itcast.cn'

# 运行蜘蛛
scrapy crawl  mingyan
