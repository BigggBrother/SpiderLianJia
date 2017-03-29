# -*-coding: utf-8
from test1 import download
from pymongo import MongoClient
from test1 import MongoCache
import datetime

print datetime.timedelta(minutes = 2)

links = ['a1','b2','c3','d4','e5','f6','g7',
'h8','i9','j10','k11','l12','m13','n14','o15',]
for i in xrange(len(links)):
    print i
    # print links[i]
    links.pop(0)
    print links
# while True:
#     try:
#         link = links.pop()
#         print links
#     except:
#         break
#
# n = len(links)
# for i in range(n):
#     links.pop()
#     print links