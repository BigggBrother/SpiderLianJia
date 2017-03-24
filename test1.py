# -*-coding: utf-8
import urllib2
import re
import itertools
import urlparse
import time
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


def get_links(url,regex):
    links = soup.find_all(name="a")
    link_list = []
    for link in links:
        link_string = link.get('href')
        try:
            if re.search(regex, link_string):
                link = urlparse.urljoin(url, link_string)
                if link not in link_list:
                    link_list.append(link)
        except:
            continue
    return link_list


if __name__ == "__main__":
    # for page in itertools.count(1):
        #Line 16
    seed_url = "http://sh.lianjia.com/ditiefang/li110460733"
    html = download(seed_url)
    soup = BeautifulSoup(html,'lxml')
    regex = r'li\d+$'
    links = get_links(seed_url,regex)
    print links
    for link in links:
        regex = r'li\d+s\d+'
        html = download(link)
        soup = BeautifulSoup(html,'lxml')
        links= get_links(link,regex)
        for link in links:
            for page in itertools.count(1):
                url = link+"/d%dp22" % page
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
                    print xiaoqu,u'%s万'%price,pingfang,rights,per,metro,'%s%s'%(location[0].string,location[1].string)
