# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 15:06:09 2020

@author: Naseem
"""

import os
import math
import threading
import requests
import numpy as np
from bs4 import BeautifulSoup,NavigableString, Tag
import csv
import re
import time
from random import randrange
import pandas as pd
import pymysql
from datetime import datetime
from random import randrange
from requests.exceptions import HTTPError
from requests.exceptions import ConnectionError
from loguru import logger
#from scrapy.selector import Selector

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
           'From': 'google@google.com'}

baseUrl = 'https://www.nadaguides.com'
jdBaseUrl = 'https://www.jdpower.com'

class DBScrapperConnect():
    
    def __init__(self):
        self.conn = pymysql.connect(host='209.126.3.200', port=int(3306), 
                                    user='mi_user', passwd='ce251CwE584##878', 
                                    db='mi_dbmark', autocommit=True);
        
        self.cHandler = self.conn.cursor()
  
        
        
    def insertData(self, make, model, trim, year, miles,NADA_price,JD_price):
        added = datetime.date(datetime.now())
        sql = '''
        insert into tbl_autos
        (make, model, trim, year, miles, added, NADA_price, JD_price) 
        values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
        '''.format(make, model, trim, year, miles,added,NADA_price,JD_price)

        try:
           
           # self.cHandler.execute(sql)
           self.run_query(sql)
         
        except Exception as e: 
            print("database error: " , e)


    def getURLExtTrueCar(self):
        sql = '''
            SELECT slug, max(zip) as zip FROM truecar_ group by slug
            '''
        results = pd.read_sql_query(sql, self.conn)

        return results
    
    def getScrpedAutos(self):
        # where year ='2017' and make='Acura'
        sql = '''
             select year,make from scrapeData_  group by year, make
             '''
        resutls = pd.read_sql_query(sql, self.conn)
        return resutls
    def run_query(self, query):
            """Execute SQL query."""
            try:
                self.open_connection()
                with self.conn.cursor() as cur:  
                    cur.execute(query)
            except pymysql.MySQLError as e:
                print(e)
            finally:
                if self.conn:
                    self.conn.close()
                    self.conn = None
                    #logger.info('Database connection closed.')
    def open_connection(self):
        """Connect to MySQL Database."""
        try:
            if self.conn is None:
                self.conn = pymysql.connect(host='209.126.3.200', port=int(3306), 
                                    user='mi_user', passwd='ce251CwE584##878', 
                                    db='mi_dbmark', autocommit=True);
        except pymysql.MySQLError as e:
            logger.error(e)
            #sys.exit()
        finally:
            logger.info('Connection opened successfully.')
dbase = DBScrapperConnect()

def nada_cars(year,make):
    url = 'https://www.nadaguides.com/Cars/{}/{}'.format(year,make)
    res = getConnection(url)
    soup = BeautifulSoup(res.content, "html.parser")
    pCars = soup.find_all('div', {'class': 'col-xs-12 model-image-list__title track-autos-ymm-model-title'})
    
    print("nada cars:" + str(len(pCars)))
  
    if len(pCars) > 0 :
        #urls = pCars.find_all("a")
        for url in pCars:
            scrapeCarDetails(url.find("a")['href'])
    else:
        print(url)

def getConnection(url):
    
    triesFlag = True
    res = None
    tries = 0
    while(triesFlag):
        try:
            res = requests.get(url=url)
            triesFlag = False
        except HTTPError as con_err: 
                print(f'HTTP Error accurred: {con_err}')
                print('retring... ', tries)
                tries += 1
        except Exception as err: 
                print(f'HTTP Error accurred: {err}')
                print('retring... ', tries)
                tries += 1
        time.sleep(randrange(2,6))
    return res

def scrapeCarDetails(link):
    res = getConnection(baseUrl+link)
    soup = BeautifulSoup(res.content, "lxml")
    detailsURls = soup.find_all("a", {"class": "trim-list__link"})
    print("trims : "+ str(len(detailsURls)))
    for durl in detailsURls:
        dhref = durl['href'].replace("Zip","Values")
        carInfo = getBasicNadaValuesFromUrl(dhref)
        price_link = baseUrl+dhref
        try: 
            price = nada_price_scraper(price_link)
            carInfo['NADA_price'] = price
        except IndexError as err:
            logger.error(price_link)
            print(err)
            price = 0
        #fetch jd data.
        jdData =getMileageAndJDPrice(jdBaseUrl+dhref.replace("/Values",""))
        carInfo['JD_price'] = jdData[0]
        carInfo['miles'] = jdData[1]
        dbase.insertData(carInfo['make'], carInfo['model'], carInfo['trim'], carInfo['year'], carInfo['miles'], carInfo['NADA_price'], carInfo['JD_price'])
        print(carInfo)
        
def nada_price_scraper(link):
    url = link #'https://www.nadaguides.com/Cars/2003/Acura/NSX/2-Door-Coupe-Targa/Values' #
    nada_price = '' 
    oldLink = False
    res = getConnection(url=url)
    soup = BeautifulSoup(res.content, 'html.parser')
    #print(soup)pricing-table__totals total-invoice heading-s pricing-table__totals total-msrp heading-s
     #soup.find('div', {'class': 'pricing-table__totals total-msrp heading-s'})
    logger.info(link)
    prices = getNadaTotalBasePrice(soup)
    print(prices)
    
    if prices != 'None':
        try:
            nada_price = prices
            nada_price = nada_price.replace("$", "")
            nada_price = nada_price.replace(",", "")
        except AttributeError as err:
            print("NoneType: ", link)  
            #nada_price = getPriceFromTradInPage(soup)
    else:
        print("None: ", link)
        nada_price = 0
    print(link,nada_price)
    return nada_price
def getPriceFromTradInPage(soup):
    tags = soup.select("div[title*='Clean Retail']")
    tprices = soup.select("div[class='pricing-table__totals-row']>div")
    if(len(tags) > 0):
        price = tprices[len(tprices)-1:]
        price = price[0].get_text().replace("$","").replace(",","")
        print("price", price)
        return price
def getBasicNadaValuesFromUrl(url):
    d = url.replace("/Values","").replace("/Cars/","")
    data = d.split("/")
    car = {}
    car['year'] = data[0]
    car['make'] = data[1]
    car['model'] = data[2]
    car['trim'] = data[3]
    return car
def getMileageAndJDPrice(url):
     res = getConnection(url=url)
     soup = BeautifulSoup(res.content, 'html.parser')
     values = soup.find_all("p",{"class","value"})
     jdData = []
     try:
         price = values[0].get_text().strip().replace("$","").replace(",","")
         miles = values[1].get_text().strip().replace(",","")
         if price == "N/A":
             price = 0
         if miles == "N/A":
             miles = ''
     except:
         logger.error(url)
         price = 0
         miles = ''
     jdData.append(price)
     jdData.append(miles)
     return jdData
def dividePagesToThreads(data):
        totalPages = len(data)
        totalThreads = 5
        threads = []
        perThread = totalPages/totalThreads
        count = 0
        items = 0
        nextItems = 0
        for i in range(0, totalThreads):
            count += 1
            if count != totalThreads:
                sliceRange = math.floor(perThread)
                if nextItems == 0:
                    nextItems = sliceRange
                thread = threading.Thread(target=page_scraping, args=(data.loc[items:nextItems,], sliceRange))
                threads.append(thread)
                items += sliceRange+1
                print(items,nextItems)
                nextItems = items + sliceRange
                
            else:
                sliceRange = math.ceil(perThread)
                thread = threading.Thread(target=page_scraping, args=(data.loc[items:nextItems,], sliceRange))
                threads.append(thread)
                items += sliceRange
                print(items,nextItems)
                nextItems = items + sliceRange+1
        for thread in threads:
            thread.start()
            print("started : ",thread)
            rand = randrange(32, 120)
            time.sleep(rand)
        
        for thread in threads:
            thread.join()
            print("joined : ",thread)
        print("total items; ", items)
        
def getNadaTotalBasePrice(soup):
       pprices = getChildsOfSiblings(getTotalBasePrice(soup))
       return pprices[len(pprices)-1]
def getTotalBasePrice(soup):
        #tags = soup.select("div[title*='Clean Retail']")
        #tprices = soup.select("div[class='pricing-table__totals-row']>div")
        div = soup.find('div',string="Total Base Price") 
        if div == None: 
            div = soup.find('div', string="Base Price")
            print("divs base price", div)
        return div.next_siblings
def getChildsOfSiblings(siblings):
    child = []
    for c in siblings:
        if isinstance(c, NavigableString):
            continue
        if isinstance(c, Tag):     
            child.append(c.get_text())
    print("Total Base Price", child)
    return child
def page_scraping(page, data):
        cars = page
        for ind in cars.index:
            #price = nada_price_scraper(cars['year'][ind], cars['make'][ind], cars['model'][ind], cars['trim'][ind])
            nada_cars(cars['year'][ind], cars['make'][ind])
        
cars = dbase.getScrpedAutos()
dividePagesToThreads(cars)
#page_scraping(cars,2)