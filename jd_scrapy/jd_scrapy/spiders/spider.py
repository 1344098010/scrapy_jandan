#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
爬取的是煎蛋网上的妹子图片
'''
import re
import scrapy
from scrapy import Request
import requests
from lxml import etree
import base64


class InfoSpider(scrapy.Spider) :

    # 该爬虫的名字
    name = "jiandan"
    start_url = 'http://jandan.net/ooxx/page-1#comments'
    next_page = ''
    headers = {'referer': 'http://jandan.net/',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'}
    # 设置计数器，以记录爬取的数据数量，方便命名本地保存的文件
    index = 1

    # start_request() 方法用来设置初始请求，可以不进行设置，但本人觉得还有有初始方法更像爬虫
    #另外，在这个方法中还可以设置cookie user-agent IP_proxy 等参数，以增强爬虫的能力
    #但煎蛋网不需要cookie 等参数，所以此处未设置

    def start_requests(self):
        # 超时设置为1秒，返回str
        html = requests.get(self.start_url, headers=self.headers, timeout=1).text
        # etree格式化
        html = etree.HTML(html)
        #使用xpath 查询图片链接 2018/8/12 煎蛋网图片的链接被隐藏，真正的链接需要用view-source:url 查看，并且使用base64加密
        for link in html.xpath('//div[@class="text"]/p/span[@class="img-hash"]/text()'):
            #构造完整url
            link = 'https:' + str(base64.b64decode(link), 'utf-8')
            #打印日志
            print('当前抓取链接:', self.next_page, '-----', link)
            with open('F:/jiandanscrapy/' + '{0}.{1}'.format(self.index, format(link[-4:])), 'wb') as jpg:
                try:
                    # 抓取数据并保存，如果链接无效，继续循环
                    r = requests.get(link, headers=self.headers, timeout=1)
                    r.raise_for_status()
                    jpg.write(r.content)
                    # 打印日志
                    print("正在抓取第%s条数据" % self.index, '文件保存为：{0}.{1}'.format(self.index, format(link[-4:])))
                except:
                    continue
            self.index += 1
        # 查询下一页链接，不为空则进入parse循环
        self.next_page = 'https:' + str(html.xpath('//div[@class="comments"]/div[@class="cp-pagenavi"]/a[@title="Newer Comments"]/@href')[1])
        if self.next_page is not None:
            yield Request(self.next_page, callback=self.parse)
     #<end start_request>


    # parse 方法通过 Request中的callback调用
    def parse(self, response):
        # 解码respone
        response = response.text
        # etree格式化response
        html = etree.HTML(response)
        # 下面的for循环和上面一样
        for link in html.xpath('//div[@class="text"]/p/span[@class="img-hash"]/text()'):
            link = 'https:' + str(base64.b64decode(link), 'utf-8')
            print('当前抓取链接:', self.next_page, '-----', link)
            with open('F:/jiandanscrapy/' + '{0}.{1}'.format(self.index, format(link[-4:])), 'wb') as jpg:
                try:
                    r = requests.get(link,headers=self.headers, timeout=1)
                    r.raise_for_status()
                    jpg.write(r.content)
                    print("正在抓取第%s条数据" % self.index, '文件保存为：{0}.{1}'.format(self.index, format(link[-4:])))
                except:
                    continue
            self.index += 1

        # 同样构造下一页url
        self.next_page = 'https:' + str(html.xpath('//div[@class="comments"]/div[@class="cp-pagenavi"]/a[@title="Newer Comments"]/@href')[1])
        if self.next_page is not None:
            # yield 回调parse
            yield Request(self.next_page, callback=self.parse)
    #<end parse>
