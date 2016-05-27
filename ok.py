#coding = utf8
import re
import requests
import urllib,urllib2
from BeautifulSoup import BeautifulSoup

url = 'https://www.so.com/s?q=02081452010'
page = urllib2.urlopen(url)
soup = BeautifulSoup(page)
htmlList = soup.findAll('span',{'style':'color:#cc0000;'})

a = htmlList[0].find('b')
print a.text