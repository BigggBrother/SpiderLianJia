# -*-coding: utf-8
import re
import json
import time
import hashlib
import urllib2
import urlparse
import itertools
import threading
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime, timedelta
from setting import db_host, db_port, max_thread



def download(url,num_retires = 2):
    print 'Downloading: ', url
    record = conn.getitem(url)
    if record:
        html = record['result']
    if not record:
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

def crawler(link, regex):
    html = download(link)
    soup = BeautifulSoup(html,'lxml')
    links = get_links(link, soup, regex)
    for link in links:
        for page in itertools.count(1):
            url = link + "/d%dp22" % page
            html = download(url)
            soup = BeautifulSoup(html, 'lxml')
            house_list = soup.select('ul.house-lst > li')
            if not house_list or soup.find(attrs={'class': 'list-no-data clear'}):
                break

            for house in house_list:
                try:
                    metro_list = soup.find_all(attrs={'class': 'js_condition'})
                    msg = {
                        'xiaoqu': house.find(attrs={'class': 'laisuzhou'}).string,
                        'price': house.find(attrs={'class': 'num'}).string,
                        'pingfang': house.select('div.where > span')[1].string,
                        'per': house.find(attrs={'class': 'price-pre'}).string,
                        'location': '%s%s' % (
                        house.select('div.con > a')[0].string, house.select('div.con > a')[1].string),
                        'metro': metro_list[0].string,
                        'station': metro_list[1].string,
                        'rights': house.select('span.taxfree-ex > span')[0].string,
                        'createtime': datetime.now()
                    }
                except:
                    continue
                conn.insert_house(msg)
                print msg


def get_links(url, soup, regex):
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

class MongoCache:
    def __init__(self, client=MongoClient(db_host, db_port), expires=timedelta(days=1)):
        self.client = client
        self.db = client.cache
        self.db.webpage.create_index('createtime',
            expireAfterSeconds=expires.total_seconds())

    def getitem(self, url):
        return self.db.webpage.find_one({'_id': url})

    def setitem(self, url, result):
        record = {'url': url, 'result': result, 'createtime': datetime.utcnow()}
        self.db.webpage.update({'_id': url}, {'$set': record}, upsert=True)

    def insert_house(self,msg):
        string = msg['xiaoqu']+msg['price']+msg['pingfang']+msg['per']+msg['location']+msg['metro']+msg['station']+msg['rights']
        hash_key = hash_value(string)
        self.db.house.update({'_id': hash_key}, {'$set': msg}, upsert=True)

def hash_value(msg):
    #for generating Mongo id
    string = json.dumps(msg)
    m = hashlib.sha1()
    m.update(string)
    return m.hexdigest()

def multidownloader(links):
    try:
        url = links.pop()
    except IndexError:
        pass



if __name__ == "__main__":
    # #For All Lines
    threads = []
    conn = MongoCache()
    stime = datetime.now()
    seed_url = "http://sh.lianjia.com/ditiefang/"
    html = download(seed_url)
    soup = BeautifulSoup(html,'lxml')
    regex = r'li\d+$'
    links = get_links(seed_url, soup, regex)

    while links or threads:
        regex = r'li\d+s\d+'
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)

        while len(threads) < max_thread and links:
            link = links.pop()
            thread = threading.Thread(target=crawler, args=(link, regex,))
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)
        time.sleep(1)

