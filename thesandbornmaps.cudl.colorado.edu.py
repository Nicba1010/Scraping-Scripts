#!/usr/bin/env python
import urllib2, sys, re, getopt
from bs4 import BeautifulSoup
from functions import getSoup, fileDl, ensureDir, roundUpTo, roundDownTo

baseUrl = "http://cudl.colorado.edu/luna/servlet/view/all?sort=city%2Cdate%2Csheet&os="
baseDir = "/root/maps/"

def usage():
	print("University of Colorado Sanborn Maps Scraper. Requested by /u/WhiskeyQuebec. Made by /u/nicba1010.")
	print("Specify directory or it'll all go to your root folder!!!")
	print("Options available: ")
	print("\t-s, --simple\tConstructs the simple/flat directory structure")
	print("\t-h, --help\tShows this text")
	print("\t--from\t\tStart at the given document number")
	print("\t--to\t\tEnd with the given document number")

startDoc = 0
endDoc = -1
simple = False

try:
	opts, args = getopt.getopt(sys.argv[1:], "hs", ["help", "simple", "from=", "to=", "save-dir="])
except getopt.GetoptError as err:
	print str(err)
	usage()
	sys.exit()

for o, a in opts:
	if o in ("-s", "--simple"):
		simple = True
	elif o in ("-h", "--help"):
		usage()
		sys.exit()
	elif o == "--from":
		startDoc = int(a)
	elif o == "--to":
		endDoc = int(a)
	elif o == "--save-dir":
		baseDir = a
	else:
		usage()
		assert False, "unhandled option"
		sys.exit()
		
ensureDir(baseDir)
documentSoup = getSoup(baseUrl + "0")
documentTotal = int(documentSoup.find('div', { "id" : "PageRange" }).text.split('of')[1].strip().replace(',',''))
print str(documentTotal) + " documents to download. Let's get started!"
if endDoc == -1:
	endDoc = documentTotal

documetNum = 1
print("Scanning range from " + str(roundDownTo(startDoc, 50)) + " to " + str(documentTotal if roundUpTo(endDoc, 50) > documentTotal else roundUpTo(endDoc, 50)))
for i in range(roundDownTo(startDoc, 50), documentTotal if roundUpTo(endDoc, 50) > documentTotal else roundUpTo(endDoc, 50), 50):
	print("Documents " + str(i) + " to " + str(i+50))
	groupSoup = getSoup(baseUrl + str(i))
	for mediaContainer in groupSoup.findAll('div', { "class" : "mediaContainer" }):
		if documetNum < startDoc:
			documetNum += 1
			continue
		elif documetNum > endDoc:
			print("My job here is done!")
			sys.exit(420)
		print("\tDocument " + str(documetNum))
		documetNum += 1
		blockQuotes = mediaContainer.findAll('blockquote')
		try:
			print("\t\tCity: \t\t" + blockQuotes[0].text.strip())
			print("\t\tDate: \t\t" + blockQuotes[1].text.strip())
			print("\t\tSheet: \t\t" + blockQuotes[2].text.strip())
		except Exception:
			pass
		singleDocumentUrl = mediaContainer.find('a')['href']
		print("\t\tDoc Url: \t" + singleDocumentUrl)
		singleDocumentSoup = getSoup(singleDocumentUrl)
		theJavaScript = singleDocumentSoup.find('div', { "class" : "controlStrip" }).nextSibling.nextSibling
		theJP2Url = str(theJavaScript).split("openPdfInWindow")[1].splitlines()[5].strip()[11:-38]
		print("\t\tJP2 Url: \t" + theJP2Url)
		theXMLUrl = singleDocumentSoup.find('td', text=re.compile(r'METS XML View')).parent.nextSibling.nextSibling.find('a')['href']
		print("\t\tXML Url: \t" + str(theXMLUrl))
		if not simple:
			ensureDir(baseDir + blockQuotes[0].text.strip() + "/" + blockQuotes[1].text.strip() + "/")
		fileDl(theXMLUrl, baseDir if simple else (baseDir + blockQuotes[0].text.strip() + "/" + blockQuotes[1].text.strip() + "/"), "\t\t\t")
		theXMLId = theJP2Url.split('/')[-1][:-4]
		print("\t\tXML ID: \t" + theXMLId)
		xmlSoup = getSoup(theXMLUrl)
		admId = xmlSoup.find('filegrp').find('file', { "id" : theXMLId })['admid']
		imageWidth = int(xmlSoup.find('techmd', { "id" : admId }).find('imagewidth').text.strip())
		imageHeight = int(xmlSoup.find('techmd', { "id" : admId }).find('imagelength').text.strip())
		print("\t\tWidth: \t\t" + str(imageWidth))
		print("\t\tHeight: \t" + str(imageHeight))
		finalUrl = theJP2Url + "&x=0&y=0&width=" + str(imageWidth) + "&height=" + str(imageHeight)
		print("\t\tFinal Url: \t" + finalUrl)
		fileDl(finalUrl, baseDir if simple else (baseDir + blockQuotes[0].text.strip() + "/" + blockQuotes[1].text.strip() + "/"), "\t\t\t", theXMLId + ".jp2")
