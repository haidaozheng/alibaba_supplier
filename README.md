# alibaba_supplier
利用scrapy，根据指定关键词例如：['phone glass','shooes','dresses women']，在https://www.alibaba.com 上爬取热门供应商基本信息（公司名称、地址等）。

为了防止封IP，采用了代理（蘑菇代理的隧道代理）。

如果使用的话，需要自定义的部分：
- 请修改搜索关键词的csv文件，并在alibaba_test.py中修改为相应的地址
- 在middle_ware.py设置自己的代理信息
