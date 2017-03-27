# -*-coding: utf-8
import re
import urllib2
import urlparse
import itertools
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
from setting import db_host, db_name, db_port

def download(url,num_retires = 2):
    print 'Downloading: ', url
    conn = Mongo()
    record = conn.getitem(url)
    if record:
        html = record['result']
    else:
        try:
            html = urllib2.urlopen(url).read()
        except urllib2.URLError as e:
            print 'Download error: ', e.reason
            html = None
            if num_retires > 0:
                if hasattr(e, 'code') and 500 <= e.code < 600:
                    return download(url, num_retires-1)
    conn.setitem(url, html)
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

class Mongo:
    def __init__(self,client= MongoClient('192.2.4.166', 27017)):
        self.client = client
        self.db = client.cache
    def getitem(self, url):
        self.db.webpage.find_one({'id': url})
        # if record:
        #     return record['result']
        # else:
        #
        #     raise KeyError(url + ' dos not exist')
    def setitem(self, url, result):
        record = {'url': url, 'result': result}
        self.db.webpage.update({'_id': url}, {'$set': record}, upsert=True)

def mongo(db_host, db_name, db_port = 27017):
    conn = MongoClient(db_host, db_port)



if __name__ == "__main__":
    # for page in itertools.count(1):
        #Line 16
    stime = datetime.now()
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
                        metro_list = soup.find_all(attrs={'class':'js_condition'})
                        msg = {
                            'xiaoqu': house.find(attrs = {'class':'laisuzhou'}).string,
                            'price' : house.find(attrs = {'class':'num'}).string,
                            'pingfang' : house.select('div.where > span')[1].string,
                            'per' : house.find(attrs = {'class':'price-pre'}).string,
                            'location' : '%s%s'%(house.select('div.con > a')[0].string,house.select('div.con > a')[1].string),
                            'metro': metro_list[0].string,
                            'station': metro_list[1].string,
                            'rights' : house.select('span.taxfree-ex > span')[0].string,
                        }
                    except:
                        continue
                    print msg
    time_duration = datetime.now() - stime
    print time_duration
