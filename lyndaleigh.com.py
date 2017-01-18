#!/usr/bin/python3

from requests.auth import HTTPBasicAuth
import requests
import sys
from bs4 import BeautifulSoup
import getpass
import time

def sCodeChk(resp, prepend = ""):
	if DEBUG:
		print(prepend + "URL: {}\n".format(resp.url) + prepend + "  Response Code: {:3d}".format(resp.status_code))
	return resp.status_code
def ensureLoad(url, s, prepend = ""):
	loaded = s.get(url)
	bs = BeautifulSoup(loaded.content, 'lxml')
	if sCodeChk(loaded, prepend) != 200 or len(bs.prettify()) < 400:
		print(prepend + "Retrying in 5 seconds... Bs Size " + str(len(bs.prettify())))
		time.sleep(5)
		loaded = ensureLoad(url, s) #Recursive call
	return loaded

base = "http://lyndaleigh.com"
base_url = base + "/members/"
session = requests.Session()

username = input("Username: ")
password = getpass.getpass("Password: ")
DEBUG = True

session.auth = (username, password)

latest = ensureLoad(base_url + "index.php/latest-updates.html", session)

while sCodeChk(latest) == 500:
	print("Sleeping for 5 seconds...")
	time.sleep(5)
	latest = session.get(base_url + "index.php/latest-updates.html")

latest_soup = BeautifulSoup(latest.content, 'lxml')
last_page = int(int(latest_soup.find('a', { 'title' : "End" })['href'].split('=')[-1]) / 45)

base_gallery_url = base_url + "index.php/latest-updates.html?start="

for page in range(last_page + 1):
	gallery_page_url = base_gallery_url + str(page * 45)
	gallery_page = ensureLoad(gallery_page_url, session)
	gallery_page_soup = BeautifulSoup(gallery_page.content, 'lxml')
	item_num = 0
	for item in gallery_page_soup.findAll('div', { 'class' : 'itemContainer' }):
		#print(item.prettify())
		item_num = item_num + 1
		item_type = item.findAll('img', { 'class' : 'uk-responsive-width uk-align-center' })[0]['alt']
		is_video = True if item_type == "Lynda Leigh Video Update" else False
		item_url = base + item.find('a', { 'class' : 'uk-thumbnail' })['href']
		item_text_part = item.find('div', { 'class' : 'uk-thumbnail-caption' })
		item_title = item_text_part.findAll('strong')[0].text.strip()
		item_desc = item_text_part.find('span', { 'style' : ['font-size: 8pt; line-height: 6px;', 'font-size:9pt;', 'font-size: 8pt; line-height: 5px;', 'font-size: 9pt'] }).text.strip()
		
		print('Page {:2d} item {:2d}\n\tType: \t{}\n\tTitle: \t{}\n\tDesc: \t{}'.format(page + 1, item_num, item_type, item_title, item_desc))
		#print("Page " + str(page + 1) + " item " + str(item_num) + "\nType: \t" + item_type + "\nTitle: \t" + item_title + "\nDesc: \t" + item_desc)
		
		item_page = ensureLoad(item_url, session, "\t")
		item_page_soup = BeautifulSoup(item_page.content, 'lxml')
		if is_video:
			#VIDEO DOWNLOAD AND PARSE
			try:
				high_res_dl = base + item_page_soup.find(text='1080p MPEG').parent.parent['href']
			except AttributeError:
				print(item_page_soup.prettify())
				print(str(len(item_page_soup.prettify())))
			print(high_res_dl)
		else:
			#PHOTO DOWNLOAD AND PARSE
			high_res_dl = ""
			try:
				high_res_dl = base + item_page_soup.find(text='Hi Res').parent['href']
			except AttributeError:
				try:
					high_res_dl = base + item_page_soup.find(text='Web Res').parent['href']
				except AttributeError:
					try:
						high_res_dl = base + item_page_soup.find(text='Med Res').parent['href']
					except AttributeError:
						try:
							high_res_dl = base + item_page_soup.find(text='Low Res').parent['href']
						except AttributeError:
							print(item_page_soup.prettify())
							print(str(len(item_page_soup.prettify())))
			print(high_res_dl)
