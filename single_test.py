# -*-coding: utf-8
import urllib2
import re
import itertools
from bs4 import BeautifulSoup

def download(url,num_retires = 2):
    print 'Downloading: ', url
    try:
        html = urllib2.urlopen(url).read()
    except urllib2.URLError as e:
        print 'Download error: ', e.reason
        html = None
        if num_retires > 0 :
            if hasattr(e,'code') and 500<=e.code<600:
                return download(url, num_retires-1)
    return html

def link_crawler(seed_url, link_regex):
    '''Crawl from the given seed URL following links matched by link_regex'''
    crawl_queue = [seed_url]
    while crawl_queue:
        url = crawl_queue.pop()
        html = download(url)
        for link in get_links(html):
            if re.match(link_regex,link):
                crawl_queue.append(link)

def get_links(html):
    webpage_regex = re.compile('<a[^>]+href= ["\'](.*?)["\']',re.IGNORECASE)
    return webpage_regex.findall(html)

if __name__ == "__main__":
    for page in itertools.count(1):
        url = "http://sh.lianjia.com/ditiefang/li110460733s100021855/d%d"%page
        html = download(url)
        soup = BeautifulSoup(html,'lxml')
        house_list = soup.select('ul.house-lst > li')
        if not house_list or soup.find(attrs={'class':'list-no-data clear'}):
            break

        for house in house_list:
            try:
                xiaoqu = house.find(attrs = {'class':'laisuzhou'}).string
                price = int(house.find(attrs = {'class':'num'}).string)
                pingfang = house.select('div.where > span')[1].string
                per = house.find(attrs = {'class':'price-pre'}).string
                location = house.select('div.con > a')
                metro = house.find(attrs = {'class':'fang-subway-ex'}).string
                rights =house.select('span.taxfree-ex > span')[0].string
            except:
                continue
            # if 200<=price<=300:
            print xiaoqu,u'%s万'%price,pingfang,rights,per,metro,'%s%s'%(location[0].string,location[1].string)

        # for xiaoqu in where:
        #     print xiaoqu.string
        # for link in div.find_all('a'):
        #     print link.get('href')
        # link_regex = '/(index|view)/'
        # link_crawler(seed_url,link_regex)