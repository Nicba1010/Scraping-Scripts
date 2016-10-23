#!/usr/bin/env python
import urllib2, base64, sys, re, os, json
from bs4 import BeautifulSoup
from functions import outputcolors, ensureDir, fileDlWithAuth

if len(sys.argv) != 4:
	print("Scraping script for pantyhoseplaza.com porn size.")
	print("Usage:\n\tpython pantyhoseplaza.com.py pageNumber username password")
	sys.exit()
username = sys.argv[2]
password = sys.argv[3]
baseUrl = "http://www.pantyhoseplaza.com/members/"
baseDir = "/mnt/san/"
regex = re.compile(".*Format.*")

request = urllib2.Request(baseUrl + "content.php?show=videos&section=37&page=" + sys.argv[1])
base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
request.add_header("Authorization", "Basic %s" % base64string)   
result = urllib2.urlopen(request)

rootSoup = BeautifulSoup(result, "lxml")

for table in rootSoup.findAll('table', { "bgcolor" : "#1d1d1d" }):
	anchor = table.find('a', { "style" : "color:#FF0000" })
	name = anchor.text.strip()
	videoUrl = baseUrl + anchor['href']
	description = table.findAll('tr')[1].find('div').text.strip()
	dirName = baseDir + "pantyhoseplaza.com/" + name.replace(":", "")
	ensureDir(dirName)
	print(name + "\n\t" + videoUrl)
	requestVid = urllib2.Request(videoUrl)
	requestVid.add_header("Authorization", "Basic %s" % base64string)
	resultVid = urllib2.urlopen(requestVid)
	vidSoup = BeautifulSoup(resultVid, "lxml")
	imageUrl = baseUrl + vidSoup.find('img', { "style" : "border-color:#990000" })['src']
	print("\tIMAGE: " + imageUrl)
	fileDlWithAuth(imageUrl, base64string, dirName + "/", "\t")
	data = {'Name' : name, 'Description' : description}
	with open(dirName + '/data.json', 'w') as outfile:
    		json.dump(data, outfile)
	for vidDiv in vidSoup.findAll('div'):
		if regex.match(vidDiv.text.strip()):
			trueVideoUrl = baseUrl + vidDiv.find('a')['href']
			videoSize = vidDiv.findAll('a')[1].text.strip()
			print("\t\t" + videoSize + " => " + trueVideoUrl)
			trueVidRequest = urllib2.Request(trueVideoUrl)
			trueVidRequest.add_header("Authorization", "Basic %s" % base64string)
			trueVidResult = urllib2.urlopen(trueVidRequest)
			trueVidSoup = BeautifulSoup(trueVidResult, "lxml")
			trueVideoDownloadUrl = baseUrl + trueVidSoup.find('a', text="Click here to download the full length video!")['href']
			print("\t\t\tVIDEO SOURCE URL: " + trueVideoDownloadUrl)
			fileDlWithAuth(trueVideoDownloadUrl, base64string, dirName + "/", "\t\t\t")
