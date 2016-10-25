#!/usr/bin/env python
from __future__ import division
import sys
from datetime import datetime
from functions import getSoup, getStatus, fileDl, ensureDir

baseDir = "/root/thechive.com/"
baseUrl = "http://thechive.com/page/"
filter = ("Photo", "Photos", "photos", "photo")

def findLastPage(increment = 1000, last = 0, lastStatus = 200):
	imul = 1
	if lastStatus == 200:
		shouldBe = 404
	else:
		shouldBe = 200
		imul = -1
	lastPlusInc = increment * imul + last
	newStatus = getStatus(baseUrl + str(lastPlusInc) + "/")
	newIncr = increment // 2 if shouldBe == newStatus else increment
	print ("\t" + str(newStatus) + " @ " + str(lastPlusInc) + " next status should be " + str(shouldBe) + ", in/decrement will be " + str(newIncr))
	if increment == 1:
		if lastStatus == 200:
			if getStatus(baseUrl + str(last + 1) + "/") == 404:
				return last
		newIncr = 1
	return findLastPage(newIncr, lastPlusInc, newStatus)

print("Invoking findLastPage()")
lastPage = findLastPage()
print("Last page is " + str(lastPage))

for page in range(0, lastPage + 1):
	pageSoup = getSoup("http://thechive.com/page/" + str(page) + "/")
	print("Page " + str(page) + " of " + str(lastPage))
	for article in pageSoup.findAll('article', { "role" : "article" }):
		date = article.find('time').text.strip()
		h3 = article.find('h3', { "class" : "post-title entry-title card-title" })
		name = h3.text.strip()
		url = h3.find('a')['href']
		if any(x in name for x in filter):
			print("\tName: " + name + "\n\t\tDate: " + date)
			dateFolder = "NonParsable/"
			try:
				dateFolder = datetime.strptime(date, '%b %d, %Y').strftime("%Y/%m/%d/")
			except ValueError:
				print("\t\tGoing to NonParsable folder")
			ensureDir(baseDir + dateFolder + name + "/")
			postSoup = getSoup(url)
			for countTag in postSoup.findAll('div', { "class" : "count-tag" }):
				try:
					img = countTag.parent.find('img')
					imgSrc = img['src'].split('?')[0] + "?quality=100"
					imgName = img['src'].split('?')[0].split('/')[-1]
					if any(x in img['class'] for x in { "gif-animate" }):
						imgSrc = img['data-gifsrc'].split('?')[0]
						imgName = img['data-gifsrc'].split('?')[0].split('/')[-1]
					print("\t\t\tImage" + countTag.text + ": " + imgSrc)
					fileDl(imgSrc, baseDir + dateFolder + name + "/", "\t\t\t\t", imgName)
				except:
					
					pass
