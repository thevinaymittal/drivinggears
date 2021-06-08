# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 10:13:14 2020

@author: nanshu yi
"""

#!/usr/bin/env python3

"""salesScraper.py: Pulls data from all CarMax sales listings and exports to a file called salesListingsCurrent.csv."""
import csv
import furl
import logging
import math
import json
import time
from selenium import webdriver

logging.basicConfig(filename='carmax-sales-data.log',format='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S',level=logging.INFO)

baseUrl = "https://www.carmax.com/cars/api/search/run"
#params = {"uri": "/cars?price=200000","skip": 0,"take": 1000, "radius": 250000, "zipCode": 91362, "sort": 20}
params = {"uri": "/cars?","skip": 0, "zipCode": 91362, "radius": 250000, "sort": 20}

exportCSVFilename = 'salesListingsCurrent.csv'

def constructUrl():
    global baseUrl
    global params

    f = furl.furl(baseUrl)
    f.args = params
    return f.url

def extractJsonFromSeleniumSource():
    global driver

    data = {}

    try:
        pre = driver.find_element_by_tag_name("pre").text
        data = json.loads(pre)
    except:
        print("Exception extracting JSON data, trying again in 20sec")
        logging.warning("CarMax Server Error while scraping, waiting to try again")
        time.sleep(20)
        driver.get(constructUrl())
        extractJsonFromSeleniumSource()

    return data

def addEntriesToList(data):
#    global allItemsForSale

    itemSaleList = data["items"]
    ret = len(itemSaleList);
    for i in range(len(itemSaleList)):
        with open('carmax.csv', 'a') as fp:
            wr = csv.writer(fp, lineterminator='\r')
            wr.writerow([itemSaleList[i]['make'], itemSaleList[i]['model'], itemSaleList[i]['trim'], itemSaleList[i]['year'], itemSaleList[i]['mileage'], itemSaleList[i]['basePrice'], ''])
        #print(itemSaleList[i]['make'] + " : " + itemSaleList[i]['model'] + " : " + itemSaleList[i]['trim'] + " : " + str(itemSaleList[i]['year']) + " : "+ str(itemSaleList[i]['mileage']) + " : "+ str(itemSaleList[i]['basePrice']))
    return ret;
#    print(len(allItemsForSale))

#options = webdriver.ChromeOptions()
# pass in headless argument to options
#options.add_argument('--headless')
#driver = webdriver.Chrome('C:\Program Files (x86)\Google\Chrome\Application\\chromedriver.exe',chrome_options=options)

#region Selenium Init
driver = webdriver.Chrome('C:\Program Files (x86)\Google\Chrome\Application\\chromedriver.exe')

driver.get(constructUrl())
#endregion

#region Display total CarMax listings
totalListingsToGet = extractJsonFromSeleniumSource()["totalCount"]
print("Listings to scrape: " + str(totalListingsToGet))
#endregion

logging.info("STARTED Scraping " + str(totalListingsToGet) + " listings")

#region Scrape all car listings
#allItemsForSale = []
with open('carmax.csv', 'w' , newline = '') as csvfile:
   fieldnames = ['Make', 'Model', 'Trim', 'Year', 'Miles', 'Price','Url'];
   writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
   writer.writeheader()

#for i in range(math.floor(totalListingsToGet / 1000)):
while True:   
    driver.get(constructUrl())

    readCounts = addEntriesToList(extractJsonFromSeleniumSource())

    time.sleep(2)

    params["skip"] += readCounts;
    
    if params["skip"] >= totalListingsToGet:
        break

params["take"] = (totalListingsToGet % 1000)

driver.get(constructUrl())
addEntriesToList(extractJsonFromSeleniumSource())
driver.close()
#endregion

#csv.exportCSV(exportCSVFilename, allItemsForSale)

#print("Exported all listings to " + exportCSVFilename)
logging.info("SUCCESS Scraping " + str(totalListingsToGet) + " listings")








