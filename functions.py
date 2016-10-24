#!/usr/bin/env python
import urllib2, os, sys, math
from bs4 import BeautifulSoup
from datetime import timedelta, date

class outputcolors:
        OKGREEN = '\033[92m'
        OKBLUE = '\033[94m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'

def roundUpTo(x, base):
	return int(base * math.ceil(float(x) / base))

def roundDownTo(x, base):
        return int(base * math.floor(float(x) / base))

def ensureDir(f):
        if not os.path.exists(f):
                os.makedirs(f)

def replaceTab(s, tabstop = 4):
	result = str()
	for c in s:
		if c == '\t':
			while (len(result) % tabstop != 0):
				result += ' ';
		else:
			result += c    
	return result

def fileDl(url, dir, prepend, fileName = "?"):
	if fileName == "?":
		fileName = url.split('/')[-1]
        request = urllib2.Request(url)
        u = urllib2.urlopen(request)
        meta = u.info()
        fileSize = -1
        try:
                fileSize = int(meta.getheaders("Content-Length")[0])
        except Exception:
                pass
        if os.path.exists(dir + fileName):
                if os.stat(dir + fileName).st_size == fileSize:
                        print(prepend + outputcolors.OKBLUE + "File already downloaded!" + outputcolors.ENDC)
                        return
        	else:
                	print(prepend + outputcolors.WARNING + "File downloaded but not fully! Restarting download..." + outputcolors.ENDC)
	else:
		print(prepend + outputcolors.WARNING + "Downloading file")
        fileHandle = open(dir + fileName, 'wb')
        print(prepend + ("Downloading: %s Bytes: %s" % (fileName, "???" if (fileSize == -1) else fileSize)))
        fileSizeDl = 0
        blockSize = 65536
        while True:
                buffer = u.read(blockSize)
                if not buffer:
                        break
                fileSizeDl += len(buffer)
                fileHandle.write(buffer)
                status = prepend + r"%12d  [%3.2f%%]" % (fileSizeDl, -1.0 if (fileSize == -1) else (fileSizeDl * 100. / fileSize))
                status = "\r" + status 
                print status,
        fileHandle.close()
        print("\n" + prepend + outputcolors.OKGREEN + "Done :)" + outputcolors.ENDC)

def fileDlWithAuth(url, auth, dir, prepend):
        fileName = url.split('/')[-1]
        request = urllib2.Request(url)
        request.add_header("Authorization", "Basic %s" % auth)
        u = urllib2.urlopen(request)
        meta = u.info()
        fileSize = -1
        try:
                fileSize = int(meta.getheaders("Content-Length")[0])
        except Exception:
                pass
        if os.path.exists(dir + fileName):
                if os.stat(dir + fileName).st_size == fileSize:
                        print(prepend + outputcolors.OKBLUE + "File already downloaded!" + outputcolors.ENDC)
                        return
        else:
                print(prepend + outputcolors.WARNING + "File downloaded but not fully! Restarting download..." + outputcolors.ENDC)
        fileHandle = open(dir + fileName, 'wb')
        print(prepend + ("Downloading: %s Bytes: %s" % (fileName, "???" if (fileSize == -1) else fileSize)))
        fileSizeDl = 0
        blockSize = 65536
        while True:
                buffer = u.read(blockSize)
                if not buffer:
                        break
                fileSizeDl += len(buffer)
                fileHandle.write(buffer)
		status = prepend + r"%12d  [%3.2f%%]" % (fileSizeDl, -1.0 if (fileSize == -1) else (fileSizeDl * 100. / fileSize))
                status = "\r" + status
                print status,
        fileHandle.close()
        print("\n" + prepend + outputcolors.OKGREEN + "Done :)" + outputcolors.ENDC)

def getSoup(url):
	return BeautifulSoup(urllib2.urlopen(urllib2.Request(url)), "lxml")

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)
