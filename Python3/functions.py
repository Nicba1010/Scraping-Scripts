#!/usr/bin/python3
from bs4 import BeautifulSoup
import requests

def getSoup(url, data_ = {}, file = {}):
	r = requests.post(url, data=data_, files=file)
	return BeautifulSoup(r.text, 'lxml')
