#!/usr/bin/python3

from requests.auth import HTTPBasicAuth
import requests
import sys
from bs4 import BeautifulSoup
import getpass
import time
import magic
import os
import mimetypes
import re
from datetime import datetime
import json

def ensureDir(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)
def sCodeChk(resp, prepend = ""):
	if DEBUG:
		print(prepend + "URL: {}\n".format(resp.url) + prepend + "  Response Code: {:3d}".format(resp.status_code))
	return resp.status_code
def ensureLoad(url, s, prepend = ""):
	loaded = s.get(url)
	bs = BeautifulSoup(loaded.content, 'lxml')
	if sCodeChk(loaded, prepend) != 200 or len(bs.prettify()) < 400:
		print(prepend + "Retrying in 15 seconds... Bs Size " + str(len(bs.prettify())))
		time.sleep(15)
		loaded = ensureLoad(url, s) #Recursive call
	return loaded
def fileDL(url, file_name, s):
	he = 0
	with open(file_name, "wb") as f:
		print("Downloading {}...".format(file_name))
		response = s.get(url, stream=True)
		total_length = response.headers.get('content-length')
		print(response.headers)
		if total_length is None:
			f.write(response.content)
		else:
			dl = 0
			total_length = int(total_length)
			for data in response.iter_content(chunk_size=4096):
				dl += len(data)
				f.write(data)
				done = int(50 * dl / total_length)
				sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
				sys.stdout.flush()
		he = response.headers
	return he
base = "http://lyndaleigh.com"
base_url = base + "/members/"
session = requests.Session()

username = input("Username: ")
password = getpass.getpass("Password: ")
DEBUG = True
basefolder = input("Save Folder: ")

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
		item_num = item_num + 1
		item_type = item.findAll('img', { 'class' : 'uk-responsive-width uk-align-center' })[0]['alt']
		is_video = True if item_type == "Lynda Leigh Video Update" else False
		item_url = base + item.find('a', { 'class' : 'uk-thumbnail' })['href']
		item_text_part = item.find('div', { 'class' : 'uk-thumbnail-caption' })
		item_title = item_text_part.findAll('strong')[0].text.strip().replace('/', " of ")
		item_desc = item_text_part.find('span', { 'style' : ['font-size: 8pt; line-height: 6px;', 'font-size:9pt;', 'font-size: 8pt; line-height: 5px;', 'font-size: 9pt'] }).text.strip()
		item_date = ""
		try:
			item_date = (datetime.strptime(item_text_part.find(text=re.compile(r'ADDED')).parent.nextSibling.strip(), "%d-%b-%y")).strftime("%Y-%m-%d")
		except ValueError:
			item_date = (datetime.strptime(item_text_part.find(text=re.compile(r'ADDED')).parent.nextSibling.strip(), "%d-%m-%y")).strftime("%Y-%m-%d")
		print('Page {:2d} item {:2d}\n\tType: \t{}\n\tTitle: \t{}\n\tDesc: \t{}'.format(page + 1, item_num, item_type, item_title, item_desc))
		info = {'isvideo': is_video, 'url': item_url, 'name': item_title, 'description': item_desc, 'date': item_date, 'size': 0}
		item_page = ensureLoad(item_url, session, "\t")
		item_page_soup = BeautifulSoup(item_page.content, 'lxml')
		high_res_dl = ""
		if is_video and len(item_page_soup.findAll(text='Live Members ONLY..!')) == 0:
			#VIDEO DOWNLOAD AND PARSE
			try:
				high_res_dl = base + item_page_soup.find(text='1080p MPEG').parent.parent['href']
			except AttributeError:
				try:
					high_res_dl = base + item_page_soup.find(text='MPEG').parent['href']
				except AttributeError:
					try:
						high_res_dl = base + item_page_soup.find(text='HD MPEG ').parent['href']
					except AttributeError:
						try:
							high_res_dl = base + item_page_soup.find(text='MPEG 1.4gb').parent['href']
						except AttributeError:
							try:
								high_res_dl = base + item_page_soup.find(text='MP4').parent['href']
							except AttributeError:
								try:
									high_res_dl = base + item_page_soup.find(text='720p MPEG').parent.parent['href']
								except AttributeError:
									try:
										high_res_dl = base + item_page_soup.find(text='Right Click this link to save LOW RES 720p movie').parent['href']
									except AttributeError:
										try:
											high_res_dl = base + item_page_soup.find(text='HD MPEG 808mb').parent['href']
										except AttributeError:
											try:
												high_res_dl = item_page_soup.find('source')['src']
											except AttributeError:
												print("ERROR")
												exit()
			except KeyError:
				high_res_dl = base + item_page_soup.find(text='1080p MPEG').parent['href']
			if len(high_res_dl):
				directory = basefolder + item_date + " " + item_title + "/"
				ensureDir(directory)
				header = fileDL(high_res_dl, directory + item_title + ".undef", session)
				info['size'] = header.get('content-length')
				mime = magic.Magic(mime=True)
				print("\nExtension detected: " + mime.from_file(directory + item_title + ".undef"))
				os.rename(directory + item_title + ".undef", os.path.splitext(directory + item_title + ".undef")[0] + mimetypes.guess_extension(mime.from_file(directory + item_title + ".undef")))
				with open(directory + "data.json", 'w') as outfile:
					json.dump(info, outfile)
		elif len(item_page_soup.findAll(text='Live Members ONLY..!')) == 0:
			#PHOTO DOWNLOAD AND PARSE
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
							exit()
							print(item_page_soup.prettify())
							print(str(len(item_page_soup.prettify())))
			if len(high_res_dl):
				directory = basefolder + item_date + " - Gallery - " + item_title + "/"
				ensureDir(directory)
				header = fileDL(high_res_dl, directory + item_title + ".undef", session)
				info['size'] = header.get('content-length')
				mime = magic.Magic(mime=True)
				print("\nExtension detected: " + mime.from_file(directory + item_title + ".undef"))
				os.rename(directory + item_title + ".undef", os.path.splitext(directory + item_title + ".undef")[0] + mimetypes.guess_extension(mime.from_file(directory + item_title + ".undef")))
				with open(directory + "data.json", 'w') as outfile:
					json.dump(info, outfile)
