import mechanize
import os, sys
import os.path
import cookielib
from bs4 import BeautifulSoup
import html2text
from datetime import datetime
import requests
import shutil


class HeadRequest(mechanize.Request):
	def get_method(self):
		return "HEAD"


def ensureDir(f):
	if not os.path.exists(f):
		os.makedirs(f)


def videoDl(browseItem):
	coverUrl = None
	try:
		coverUrl = browseItem.find('img')['data-interchange'].split(' ')[4][1:-1]
	except:
		coverUrl = browseItem.find('img')['src']
		print("\tALT Cover:\t" + coverUrl)
	date = datetime.strptime(browseItem.find('h2').text.strip(), "%b %d, %Y")
	videoLink = browseItem.parent['href']
	videoHtml = br.open(videoLink).read()
	videoSoup = BeautifulSoup(videoHtml, 'lxml')
	wideCoverUrl = \
		videoSoup.find('div', {'id': 'mediaplayer'}).parent.findAll('script')[2].text.split('"image"')[1][3:].split(
			'"')[0]
	rowSingle = videoSoup.find('div', {'class': 'row single'})
	name = rowSingle.findAll('div', {'class': 'small-12 medium-12 large-12 columns'})[1].find('h1').text.strip()
	dropDl = videoSoup.find('ul', {'id': 'drop-download'})
	biggest = ""
	biggestSize = 0
	print(name + "\n\tURL:\t" + videoLink)
	for a in dropDl.findAll('a'):
		if int(a.text.strip().split('(')[1].split(' MB)')[0]) > biggestSize:
			biggestSize = int(a.text.strip().split('(')[1].split(' MB)')[0])
			biggest = a['href']
	print("\tSize:\t" + str(biggestSize) + "\n\tDL URL:\t" + biggest)
	dlDir = baseDir + date.strftime("%Y-%m-%d") + " - " + name + "/"
	ensureDir(dlDir)
	contentLength = str(br.open(HeadRequest(biggest)).info()).splitlines()[2].split(' ')[1].strip()
	print("\tDL Dir:\t" + dlDir)
	with open(dlDir + "page.html", "w") as htmlFile:
		htmlFile.write(videoHtml)
	try:
		br.retrieve(coverUrl.strip(), dlDir + "portrait.jpg")
	except Exception as e:
		r = requests.get(coverUrl.strip(), cookies=cj, stream=True)
		with open(dlDir + "portrait.jpg", "wb") as portraitFile:
			r.raw.decode_content = True
			shutil.copyfileobj(r.raw, portraitFile)
	try:
		br.retrieve(wideCoverUrl.strip(), dlDir + "wide.jpg")
	except Exception as e:
		r = requests.get(wideCoverUrl.strip(), cookies=cj, stream=True)
		with open(dlDir + "wide.jpg", "wb") as wideFile:
			r.raw.decode_content = True
			shutil.copyfileobj(r.raw, wideFile)
	while True:
		if os.path.isfile(dlDir + name + ".mp4"):
			if int(contentLength) > os.stat(dlDir + name + ".mp4").st_size:
				print("\tFilesize too low:\t" + str(os.stat(dlDir + name + ".mp4").st_size))
				print("\tShould be:\t\t" + contentLength)
				os.remove(dlDir + name + ".mp4")
			else:
				return
		br.retrieve(biggest, dlDir + name + ".mp4")


def galleryDl(browseItem):
	coverUrl = None
	try:
		coverUrl = browseItem.find('img')['data-interchange'].split(' ')[4][1:-1]
	except:
		coverUrl = browseItem.find('img')['src']
		print("\tALT Cover:\t" + coverUrl)
	date = datetime.strptime(browseItem.find('h2').text.strip(), "%b %d, %Y")
	videoLink = browseItem.parent['href']
	videoHtml = br.open(videoLink).read()
	videoSoup = BeautifulSoup(videoHtml, 'lxml')
	bigCoverUrl = \
		videoSoup.find('div', {'class': 'small-12 medium-12 large-6 columns media'}).find('img')['src'].replace('sml', 'lrg')
	rowSingle = videoSoup.find('div', {'class': 'row single info-fixed'})
	name = rowSingle.findAll('div', {'class': 'small-12 medium-12 large-12 columns'})[0].find('h1').text.strip()
	dropDl = rowSingle.find('ul', {'id': 'drop-download'})
	biggest = ""
	biggestSize = 0
	print(name + "\n\tURL:\t" + videoLink)
	for a in dropDl.findAll('a'):
		if int(a.text.strip().split(' ')[0]) > biggestSize:
			biggestSize = int(a.text.strip().split(' ')[0])
			biggest = a['href']
	print("\tSize:\t" + str(biggestSize) + "\n\tDL URL:\t" + biggest)
	dlDir = baseDir + date.strftime("%Y-%m-%d") + " - [Gallery] - " + name + "/"
	ensureDir(dlDir)
	contentLength = str(br.open(HeadRequest(biggest)).info()).splitlines()[2].split(' ')[1].strip()
	print("\tDL Dir:\t" + dlDir)
	with open(dlDir + "page.html", "w") as htmlFile:
		htmlFile.write(videoHtml)
	try:
		br.retrieve(coverUrl.strip(), dlDir + "portrait.jpg")
	except Exception as e:
		r = requests.get(coverUrl.strip(), cookies=cj, stream=True)
		with open(dlDir + "portrait.jpg", "wb") as portraitFile:
			r.raw.decode_content = True
			shutil.copyfileobj(r.raw, portraitFile)
	try:
		br.retrieve(bigCoverUrl.strip(), dlDir + "bigPortrait.jpg")
	except Exception as e:
		r = requests.get(coverUrl.strip(), cookies=cj, stream=True)
		with open(dlDir + "bigPortrait.jpg", "wb") as wideFile:
			r.raw.decode_content = True
			shutil.copyfileobj(r.raw, wideFile)
	while True:
		if os.path.isfile(dlDir + name + ".zip"):
			if int(contentLength) > os.stat(dlDir + name + ".zip").st_size:
				print("\tFilesize too low:\t" + str(os.stat(dlDir + name + ".zip").st_size))
				print("\tShould be:\t\t" + contentLength)
				os.remove(dlDir + name + ".zip")
			else:
				return
		br.retrieve(biggest, dlDir + name + ".zip")


# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

br.addheaders = [('User-agent', 'Chrome')]

br.open('http://x-art.com/members')

br.select_form(nr=0)

br.form['uid'] = ''
br.form['pwd'] = ''

br.submit()

baseDir = "/mnt/san/Operation X-ART/"

for i in range(1, 40):
	try:
		if sys.argv[1] == "-svid":
			continue
	except:
		pass
	pageHtml = br.open('http://www.x-art.com/members/videos/recent/All/' + str(i) + '/').read()
	pageSoup = BeautifulSoup(pageHtml, 'lxml')
	for browseItem in pageSoup.findAll('div', {'class': 'browse-item'}):
		videoDl(browseItem)

for i in reversed(range(1, 64)):
	print("Page: " + str(i))
	try:
		if sys.argv[1] == "-spic":
			continue
	except:
		pass
	pageHtml = br.open('http://www.x-art.com/members/galleries/recent/All/' + str(i) + '/').read()
	pageSoup = BeautifulSoup(pageHtml, 'lxml')
	for browseItem in pageSoup.findAll('div', {'class': 'browse-item'}):
		if len(browseItem.findAll('h2')[1].text.replace('Images', '').strip()) > 0:
			galleryDl(browseItem)
	if i < 15:
		raw_input("Press Enter to continue...")
