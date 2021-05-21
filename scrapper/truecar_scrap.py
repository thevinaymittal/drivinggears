import os
import threading
import requests
import numpy as np
from bs4 import BeautifulSoup
import csv
import re
import time
from random import randrange
import pandas as pd
import pymysql
from datetime import datetime

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


    
class DBScrapperConnect():
    def __init__(self):
        self.myDB = pymysql.connect(host='209.126.3.200', port=int(3306), 
                                    user='mi_user', passwd='ce251CwE584##878', 
                                    db='mi_dbmark', autocommit=True);
        
        self.cHandler = self.myDB.cursor()
  
        
        
    def insertData(self, make, model, trim, year, miles, Truecar_price, color, zip_code, upc_product_code, KBB_price, NADA_price):
        added = datetime.date(datetime.now())
        sql = '''
        insert into scrapeData_
        (make, model, trim, year, miles, Truecar_price, added, color, zip_code, upc_product_code, KBB_price, NADA_price) 
        values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}','{}','{}', '{}')
        '''.format(make, model, trim, year, miles, Truecar_price, added, color, zip_code, upc_product_code, KBB_price, NADA_price)

        try:
            self.cHandler.execute(sql)
        except Exception as e: 
            print(e)


    def getURLExtTrueCar(self):
        sql = '''
            SELECT slug, max(zip) as zip FROM truecar_ group by slug
            '''
        results = pd.read_sql_query(sql, self.myDB)

        return results











def urls_scraping(base_url='https://www.truecar.com/used-cars-for-sale/listings/location-thousand-oaks-ca/',
                  zip="91360"):

    threads = []

    for i in range(START_PAGE, MAX_PAGE + 1):
        pages = (base_url + '?page=' + str(i))
        thread = threading.Thread(target=page_scraping, args=(pages, zip))
        threads.append(thread)

    for thread in threads:
        thread.start()
        print("started : ",thread)
        rand = randrange(30, 120)
        time.sleep(rand)

    for thread in threads:
        thread.join()
        print("joined : ",thread)


def page_scraping(url, zip):
	print(url)
	db = DBScrapperConnect()
	response = '';
	try:
		response = requests.get(url)
		response.raise_for_status()
	except:
		return
	#    root = lxl.fromstring(response.content)
	soup = BeautifulSoup(response.content, "html.parser")
	cars = soup.find_all("div", {"data-qa": "Listings"})

	i = 0
	for dt in cars:
		try:
			url = dt.find("a", {'data-qa': 'VehicleCard'}).get('href')
			listing_id = url.split('/')[3]
			url_ = url.replace('/used-cars-for-sale/listing/','')
			upc_product_code = url_.split('/')[0]	
		except:
			url = ''
			listing_id = ''
			upc_product_code = ''

		try:
			str_str = dt.find("span", {'class': 'vehicle-header-make-model text-truncate'}).text
		except:
			str_str = ''

		try:
			print(str_str)
			carinfo = str_str.split(' ');
		except:
			carinfo = ''

		try:
			year = dt.find("span", {'class': 'vehicle-card-year font-size-1'}).text
		except:
			year = ''

		try:
			make = carinfo[0]
		except:
			make = ''
			make = make.replace("'", "")

		try:
			model = carinfo[1]
			model = model.replace("'", "")
		except:
			model = ''

		try:
			trim = dt.find("div", {'data-test': 'vehicleCardTrim'}).text
			trim = trim.replace("'", "")
		except:
			trim = ''

		try:
			miles = dt.find("div", {'data-test': 'vehicleMileage'}).text.split(' ')[0]
			miles = miles.replace(",", "")
			if miles == '':
				miles = -1
		except:
			miles = -1

		try:
			color = dt.find("div", {'data-test': 'vehicleCardColors'}).text.split(' ')[0]
		except:
			color = ""

		try:
			truecar_price = dt.find("h4", {'data-test': 'vehicleCardPricingBlockPrice'}).text
			truecar_price = truecar_price.replace("$", "")
			truecar_price = truecar_price.replace(",", "")
		except:
			truecar_price = -1

		try:
			zipcode = zip
		except:
			zipcode = ''


        
		try:
			# kbb scraper call
			kbb_price = ''
		except:
			kbb_price = ''

		try:
			nada_price = nada_price_scraper(year, make, model, trim)
		except:
			nada_price = ''


		db.insertData(make, model, trim, year, miles, truecar_price, color, zipcode, upc_product_code, kbb_price, nada_price)
        

def nada_price_scraper(year, make, model, trim):
	url = 'https://www.nadaguides.com/Cars/{}/{}/{}/{}/Pricing'.format(year,make,model,trim)

	nada_price = ''

	res = requests.get(url=url, headers=headers)
	soup = BeautifulSoup(res.content, 'html.parser')
	prices = soup.find_all('div', {'class': 'pricing-table__detail'})
	if len(prices) > 0:
		nada_price = prices[0].get_text()
		nada_price = nada_price.replace("$", "")
		nada_price = nada_price.replace(",", "")
	return nada_price







START_PAGE = 20
MAX_PAGE = 30  # 333
base_url = "https://www.truecar.com/used-cars-for-sale/listings/location-"


dbase = DBScrapperConnect()
url = dbase.getURLExtTrueCar()
print(len(url))
for i in range(len(url)):
    url_now = base_url + url.iloc[i]['slug'] + '/'
    zipcode = str(url.iloc[i]['zip'])
    urls = urls_scraping(url_now, zipcode)
    print(url_now)

