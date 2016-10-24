#!/usr/bin/env python
from __future__ import division
import sys
from datetime import datetime
from functions import getSoup, getStatus

baseUrl = "http://thechive.com/page/"

def findLastPage(increment = 1000, last = 0, lastStatus = 200):
	if lastStatus == 200:
		shouldBe = 404
	else:
		shouldBe = 200
	newStatus = getStatus(baseUrl + str(last + (increment if shouldBe == 404 else (increment * -1))) + "/")
	print (str(newStatus) + " @ " + str(last + (increment if shouldBe == 404 else (increment * -1))))
	if increment == 1:
		if lastStatus == 200:
			if getStatus(baseUrl + str(last + 1) + "/") == 404:
				return last
	return findLastPage(increment if shouldBe == newStatus else increment // 2, last + (increment if shouldBe == 200 else (increment * -1)), newStatus)
		
print str(findLastPage())
sys.exit()

pageSoup = getSoup("http://thechive.com/page/2320/")
for article in pageSoup.findAll('article', { "role" : "article" }):
	date = article.find('time').text.strip()
	name = article.find('h3', { "class" : "post-title entry-title card-title" }).text.strip()
	print("\tName: " + name + "\n\t\tDate: " + date)
