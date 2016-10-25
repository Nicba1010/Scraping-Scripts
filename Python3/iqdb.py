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
#image = {'file': open(imageFile, 'rb')}
#req = requests.post("http://iqdb.org/", files=image)
print(iqdbSoup.prettify())
