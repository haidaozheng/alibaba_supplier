# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import re
import pandas as pd



class AlibabaTestSpider(scrapy.Spider):
    name = 'alibaba_test'

    def start_requests(self):
        url_head = 'https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText='
        url_tail = '&viewtype=L'
        search_list = pd.read_csv(r'C:\Users\yuxin\OneDrive\Scrapy\alibaba_test\search_list.csv')
        for search_li in search_list['search_list']:
            search_url = url_head + search_li.replace(' ', '+') + url_tail
            print('-' * 20, '请求页面：')
            print(search_url)
            print('-' * 20)
            yield Request(search_url,meta = {'search_info':search_li},callback=self.parse)

    # 解析搜索页面
    def parse(self, response):
        search_info = response.meta['search_info']
        print('-'*20,'请求页面：')
        print(search_info)
        print('-'*20)

        # 第1个供应商
        if response.css('div[data-content=abox-ProductNormalList] div.m-product-item div.supplier a'):
            supplier = {}
            li = response.css('div[data-content=abox-ProductNormalList] div.m-product-item div.supplier a')
            supplier_name = li.css('::text').extract_first().strip()
            supplier_url = li.css('::attr(href)').extract_first()
            supplier_url = 'https:' + supplier_url
            supplier_url_name = re.search(r'https://(.+?)\.',supplier_url).group(1)

            supplier['search_info'] = search_info
            supplier['name'] = supplier_name
            supplier['url'] = supplier_url
            supplier['url_name'] = supplier_url_name
            yield Request(supplier_url, meta={'supplier': supplier}, callback=self.parse_supplier)

        # 第2+供应商
        ul = response.css('div[data-content=abox-ProductNormalList] div.m-product-item div.stitle.util-ellipsis a')
        for li in ul:
            supplier = {}
            supplier_name = li.css('::text').extract_first().strip()
            supplier_url = li.css('::attr(href)').extract_first()
            supplier_url = 'https:' + supplier_url
            supplier_url_name = re.search(r'https://(.+?)\.',supplier_url).group(1)

            supplier['search_info'] = search_info
            supplier['name'] = supplier_name
            supplier['url'] = supplier_url
            supplier['url_name'] = supplier_url_name
            yield Request(supplier_url,meta={'supplier':supplier},callback=self.parse_supplier)

    # 解析供应商主页
    def parse_supplier(self,response):
        supplier = response.meta['supplier']
        content = response.css('div.information-content.util-clearfix')
        if content.css('tr[data-role=companyBusinessType] td.col-value::text').extract_first():
            supplier['BusinessType'] = content.css(
                'tr[data-role=companyBusinessType] td.col-value::text').extract_first().strip()

        if content.css('tr[data-role=companyLocation] td.col-value::text').extract_first():
            supplier['Location'] = content.css('tr[data-role=companyLocation] td.col-value::text').extract_first().strip()

        if content.css('tr[data-role=supplierMainProducts] td.col-value a::text').extract_first():
            supplier['MainProducts'] = content.css('tr[data-role=supplierMainProducts] td.col-value a::text').extract_first().strip()

        # 取得供应商联系页网址
        supplier_contact_url = 'https://' + supplier['url_name'] + '.en.alibaba.com/contactinfo.html'
        yield Request(supplier_contact_url,meta={'supplier':supplier},callback=self.parse_supplier_contact)

    # 解析供应商联系页
    def parse_supplier_contact(self,response):
        supplier = response.meta['supplier']

        address = response.css('div.company-contact table.contact-table tr:nth-child(2) td.item-value::text').extract_first()
        supplier['address'] = address
        yield supplier