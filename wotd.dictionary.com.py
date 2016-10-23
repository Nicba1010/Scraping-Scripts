#!/usr/bin/env python
import urllib2, sys
from bs4 import BeautifulSoup
from functions import getSoup, daterange, fileDl, ensureDir
from datetime import date, datetime

def dlForDate(singleDate):
	print("Getting Word of the Day for: " + singleDate.strftime("%Y/%m/%d"))
        wordSoup = getSoup("http://www.dictionary.com/wordoftheday/" + singleDate.strftime("%Y/%m/%d") + "/")
        url = wordSoup.find('meta', { "property" : "og:image" })['content']
        print("\tDownloading:" + url)
        fileDl(url, sys.argv[1], "\t\t")

if (len(sys.argv) < 2) or sys.argv[1] == "--help":
	print("Scraping script for dictionary.com/wordoftheday/ first WOTD: 1999/5/3")
	print("Usage:\n\tAll until today: python wotd.dictionary.com.py \"/mnt/what/ever/directory/\"")
	print("\tSpecific date: python wotd.dictionary.com.py \"/mnt/what/ever/directory/\" yyyy/mm/dd -single")
	print("\tDate range: python wotd.dictionary.com.py \"/mnt/what/ever/directory/\" yyyy/mm/dd yyyy/mm/dd")
	sys.exit()

startDate = date(1999, 5, 3)
endDate = date.today()
ensureDir(sys.argv[1])

if len(sys.argv) == 4 and sys.argv[3] == "-single":
	startDate = datetime.strptime(sys.argv[2], "%Y/%m/%d")
	print startDate
	dlForDate(startDate)
	sys.exit()
elif len(sys.argv) == 4 and sys.argv[3] != "-single":
	startDate = datetime.strptime(sys.argv[2], "%Y/%m/%d")
	endDate = datetime.strptime(sys.argv[3], "%Y/%m/%d")

for singleDate in daterange(startDate, endDate):
	dlForDate(singleDate)
