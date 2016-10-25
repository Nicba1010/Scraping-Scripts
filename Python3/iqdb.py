#!/usr/bin/python3
import getopt, requests, sys
from bs4 import BeautifulSoup
from functions import getSoup

def usage():
	print("./iqdb.py -i <file>")

imageFile = None

try:
	opts, args = getopt.getopt(sys.argv[1:], 'hi:')
except getopt.GetoptError:
	usage()
	sys.exit(2)
for opt, arg in opts:
	if opt == '-h':
		usage()
		sys.exit()
	elif opt == '-i':
		imageFile = arg
	else:
		print("Unsupported option and/or argument")
		sys.exit(2)

print("Input file is: " + imageFile)
iqdbSoup = getSoup("http://iqdb.org/", {}, {'file': open(imageFile, 'rb')})
#print(iqdbSoup.find('div', {'class': 'pages'}).prettify())
for result in iqdbSoup.find('div', {'class': 'pages'}).findAll('table'):
	t1 = result.findAll('tr')[0].findAll('th')[0].text
	if t1 != "Your image":
		#print(result.prettify())
		print("Image Info:")
		print("\t" + t1)
		t2 = result.find('td', {'class': 'image'}).find('a')['href']
		if t2[:2] == "//":
			t2 = "http:" + t2
		print("\t\tSource:\t\t" + t2)
		t3 = result.find('img', {'class': 'service-icon'}).nextSibling
		print("\t\tSource Page:\t" + t3)
		whs = result.findAll('tr')[3].find('td').text.split(' ')
		width = int(whs[0].split('×')[0])
		height = int(whs[0].split('×')[1])
		safe = whs[1][1:-1]
		print("\t\tWidth:\t\t" + str(width))
		print("\t\tHeight:\t\t" + str(height))
		print("\t\tSafety Status:\t" + safe)
		
