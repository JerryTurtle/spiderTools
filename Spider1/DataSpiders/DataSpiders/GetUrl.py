# -*- coding=utf-8 -*-
"""
放置从一级页面的内容解析出二级url的规则函数
"""
from lxml import etree

import urllib

import time



class GetUrl:
    def __init__(self, content, head_url,info):
        self.content = content
        self.head_url = head_url
        self.info = info

    def get_content(self):
        return self.content

    def get_head_url(self):
        return self.head_url

    """
    用以解析第一类最普通的页面与第二类中使用js加载的较为普通的页面
    输入获得的html与抓取规则
    输出二级url的列表
    """
    def rule_common1(self, xpath):
        # 获取url列表，并去除列表中空项
        page = etree.HTML(self.content)
        href_list = page.xpath(xpath)
        while "" in href_list:
            href_list.remove("")
        # 将url与url_head结合为完整的url,并将一些属性信息加入
        url_list = []
        for href in href_list:
            if self.head_url != "" or self.head_url is not None:
                href = urllib.parse.urljoin(self.head_url, href)
                #print(href)
            href_info = {href: dict(url=href, task_id=self.info["task_id"],\
                                             type1=self.info["type1"], type2=self.info["type2"], \
                                             type3=self.info["type3"],type4=self.info["type4"],type5=self.info["type5"], \
                                             insert_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))}
            url_list.append(href_info)

        # for i in range(0, len(url_list)-1):
        #     url_list[i] = {url_list[i]: dict(url=url_list[i], task_id=info["task_id"],\
        #                                      type1=info["type1"], type2=info["type2"], \
        #                                      type3=info["type3"],type4=info["type4"],type5=info["type5"], \
        #                                      insert_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))}
        return url_list
