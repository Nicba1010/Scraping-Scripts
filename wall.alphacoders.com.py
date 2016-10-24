#!/usr/bin/env python
import sys, getopt
from bs4 import BeautifulSoup
from functions import getSoup, ensureDir, fileDl

def usage():
	print("wall.alphacoders.com scraping script. Made by /u/nicba1010")
	print("Options and arguments:")
	print("\t-h, --help\tShows this printout")
	print("\t--update\tStops at first found already downloaded")
	print("\t--save-dir=\tStore at this location")

bUrl = "https://wall.alphacoders.com/"
baseUrl = bUrl + "newest_wallpapers.php?page="
baseDir = "/root/wall.alphacoders.com/"
update = False
stop = False

try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "update", "save-dir="])
except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit()

for o, a in opts:
        if o == "--update":
                update = True
        elif o in ("-h", "--help"):
                usage()
                sys.exit()
        elif o == "--save-dir":
                baseDir = a
        else:
                usage()
                assert False, "unhandled option"
                sys.exit()

def processWallpaper(url):
	wallpaperSoup = getSoup(url)
	wallpaperOriginalUrl = wallpaperSoup.find('span', { "class" : "btn btn-success download-button" })['data-href']
	sys.stdout.write("\t\tOriginal Wallpaper Url: " + wallpaperOriginalUrl + "\n\t\t\t")
	categories = wallpaperSoup.find('div', { "class" : "floatright" }).findAll('strong')
	fileName = wallpaperOriginalUrl.split('/')[-4] + "." + wallpaperOriginalUrl.split('/')[-2]
	directoryStructure = baseDir
	for i in range(0, len(categories)):
		sys.stdout.write(categories[i].text.strip() + ("" if i == (len(categories) - 1) else " => "))
		directoryStructure += categories[i].text.strip() + "/"
	sys.stdout.write("\n\t\t\t\tSaving to: " + directoryStructure + fileName + "\n")
	ensureDir(directoryStructure)
	retval = fileDl(wallpaperOriginalUrl, directoryStructure, "\t\t\t\t\t", fileName)
	if int(retval) == 42 and update:
		global stop
		stop = True

wallSoup = getSoup(baseUrl + "0")
totalPages = int(wallSoup.find('ul', { "class" : "pagination pagination" }).findAll('li')[-1].find('a')['href'].split('=')[1])
for i in range(0, totalPages+1):
	print("Scraping page " + str(i) + "...")
	for thumbContainer in getSoup(baseUrl + str(i)).findAll('div', { "class" : "thumb-container-big " }):
		wallpaperUrl = bUrl + thumbContainer.find('a')['href']
		print ("\tbig.php url: " + wallpaperUrl)
		processWallpaper(wallpaperUrl)
		if stop:
			sys.exit(420)
