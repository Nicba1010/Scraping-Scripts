#!/usr/bin/env python
import sys
from bs4 import BeautifulSoup
from functions import getSoup, fileDl, ensureDir
from datetime import datetime

baseDir = "/root/econtalk.org/"
baseUrl = "http://www.econtalk.org/"
archiveSoup = getSoup(baseUrl + "archives.html")

tableRows = archiveSoup.find('div', {'class': 'archive-individual archive-date-based archive'}).findAll('tr')
for tableRow in tableRows:
	if tableRows.index(tableRow) == 0:
		continue
	date = datetime.strptime(tableRow.find('td', {'width': '5%'}).text.strip(), "%Y/%m/%d")
	extra = len(tableRow.findAll('td')[2].text.strip()) != 0
	name = tableRow.find('a').text
	dirName = date.strftime("%Y-%m-%d") + (" Extra " if extra else " ") + "- " + name + "/"
	url = tableRow.find('a')['href']
	ensureDir(baseDir + dirName)
	print(dirName[:-1])
	if not extra:
		podcastSoup = getSoup(url)
		url1 = podcastSoup.find('a', text="Download")['href']
		print("\t" + url1)
		fileDl(url1, baseDir + dirName, "\t\t")
	print("\t" + url)
	fileDl(url, baseDir + dirName, "\t\t")
