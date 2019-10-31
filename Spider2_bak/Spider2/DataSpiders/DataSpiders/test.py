import urllib.parse
head = "http://www.mod.gov.cn/regulatory/"
url = "2019-08/20/content_4848570.htm"
print(urllib.parse.urljoin(head,url))