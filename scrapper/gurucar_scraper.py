# cargurus-web-scraper

import requests
import pandas as pd
import json
import os 
from Database.dbscrapper import DBScrapperConnect
from random import randrange
import time

def scarpeGuru(zip):
	db = DBScrapperConnect()
	session = requests.Session()
	referer = 'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?sourceContext=forSaleTab_false_0&newSearchFromOverviewPage=true&inventorySearchWidgetType=AUTO&entitySelectingHelper.selectedEntity=c6079&entitySelectingHelper.selectedEntity2=c21239&zip={}&distance=50000&searchChanged=true&modelChanged=true&filtersModified=true&sortType=undefined&sortDirection=undefined'.format(zip)
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
		'Accept': 'application/json, text/javascript, */*; q=0.01',
		'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
		'Referer': referer,
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'X-Requested-With': 'XMLHttpRequest',
		}

	post = {
		'zip':zip
		}

	ajaxUrl = 'https://www.cargurus.com/Cars/inventorylisting/ajaxFetchSubsetInventoryListing.action?sourceContext=forSaleTab_false_0'

	cars = session.post(ajaxUrl,headers=headers,data=post).text
	try:
		cars = json.loads(cars)['listings']
		# exclude AMG
		for car in cars:
			if (car['zip'] == str(zip)):
				zipcode = car['zip']

				try:
					make = car['makeName']
				except:
					make = ''

				try:    
					model = car['modelName']
				except:
					model = ''
					
				try:    
					trim = car['trimName']
				except:
					trim = ''
				
				try:    
					year = car['carYear']
				except:
					year = ''
					
				try:    
					miles = car['mileage']
				except:
					miles = -1
				
				try:    
					color = car['exteriorColorName']
				except:
					color = ''
			
				try:    
					price = car['priceString']
					price = price.replace("$", "")
					price = price.replace(",", "")
				except:
					price = -1
					
				try:    
					url = car['mainPictureUrl']
				except:
					url = ''

				try:
					listing_id = car['id']
				except:
					listing_id = ''

				upc_product_code = make + '_' + model + '_' + color
				refTable = 'gurucar'
				db.insertData(make, model, trim, year, miles, price, url, color, zipcode, upc_product_code, refTable, listing_id)
	except:
		pass


dbase = DBScrapperConnect()
zipcodes = dbase.getValidZipCodes()
for i in range(len(zipcodes)):
	rand = randrange(30, 120)
	time.sleep(rand)
	scarpeGuru(zipcodes['zip'].iloc[i])