# -*-coding: utf-8
import re
html = ""
regex = re.compile('/ditiefang/li\d+s\d+')
if re.search(regex, link):
    print link