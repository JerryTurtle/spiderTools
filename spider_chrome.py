# -*- coding: utf-8 -*-

from selenium import webdriver
from lxml import etree
import time
from models import PolicySpiderTaskInfo, PolicySpiderUrlInfo
from exts import db
import urllib
import datetime

from flaskApi import get_all_content, analysis_content, insert_url

if __name__ =='__main__':
	task_id = 75
	policy_spider_task_info = PolicySpiderTaskInfo.query.filter_by(task_id=task_id)
	content_list = get_all_content(policy_spider_task_info)
	url_list = analysis_content(content_list=content_list, policy_spider_task_info=policy_spider_task_info)
	insert_url(policy_spider_task_info=policy_spider_task_info, url_list=url_list)
