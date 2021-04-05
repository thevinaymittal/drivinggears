import pandas as pd
from os import name
from flask import *
import pymysql
from datetime import datetime
import time,json
from .sqltopandas import SqlToPandas as sp
class DBConnect():
    """docstring for DBConnect"""

    def __init__(self):
        self.myDB = pymysql.connect(host='209.126.3.200', port=int(3306), 
                    user='mi_user', passwd='ce251CwE584##878', 
                    db='mi_dbmark', autocommit=True)

        self.cHandler = self.myDB.cursor()
    
    def DbConnect168(self):
        return pymysql.connect(host='162.241.85.240', port=int(3306), 
                    user='inforpti_specs', passwd='0p%%jYF7=EYc', 
                    db='inforpti_drivinggears', autocommit=True)


    def getTSR(self,VIN):
        return self.sp.getTSR(VIN)
    def getTBO(self,VIN):
        return self.sp.getTBO(VIN)
    def getTCD(self,VIN):
        return self.sp.getTCD(VIN)
    def getBFP(self,VIN):
        return self.sp.getBFP(VIN)
    def getBLP(self,VIN):
        return self.sp.getBLP(VIN)

    # 00
    def saveAutoMarketValueSearch(self,vin,miles,vehicle,price_average,price_below,price_above,certainty,mean,stdev):
            added = datetime.date(datetime.now())
            sql =   '''
                    insert into tbl_market_value (vin,miles,vehicle,price_average,price_below,price_above,certainty,mean,stdev,added) 
                    values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}','{}', '{}')
                    '''.format(vin,miles,vehicle,price_average,price_below,price_above,certainty,mean,stdev,added)
            try:    
                self.cHandler.execute(sql)
                #self.run_query(sql)   
            except Exception as e: 
                print("database error: " , e)
        
    # 02
    def checkMiles(self,miles):
        if miles<0:
            raise EOFError
        elif miles>200000:
            raise EOFError

    # 03
    def checkZip(self,zip_code):
        if zip_code<10000:
            raise EOFError
        elif zip_code>100000:
            raise "too much"
        
        sql = '''
        SELECT 
        city,state,county
        FROM 
        truecar_
        WHERE
        truecar_.zip = '{}' 
        
        '''.format(int(zip_code))

        results = pd.read_sql_query(sql, self.myDB)

        for i in range(0, len(results)):
            returnObject = {'city': str(results.iloc[i]['city']),
                            'state':str(results.iloc[i]['state']),
                            'county': str(results.iloc[i]['county'])
                            }
        return returnObject


    # 04
    def checkYear(self,year):
        if year<1997:
            raise EOFError
        elif year>2021:
            raise EOFError

    #06
    def getAvgStd(self,VINcode):
        sql = '''
                        SELECT 
                        make,model,trim, std_miles,std_true_price, avg_miles, avg_true_price,count
                        

                        FROM 
                        tbl_all_cars
                        
                        WHERE
                        vin LIKE '{}'
                        
                        '''.format(str(VINcode))
        results = pd.read_sql_query(sql, self.myDB)
        print('std ', int(results['std_true_price']),'avg10', (int(results['avg_true_price'])//10))

        if int(results['std_true_price']) < int((results['avg_true_price'])/10) :
            pass
        else:
            results['std_true_price'] = int((results['avg_true_price'])/10)

        if int(results['std_miles']):
            pass
        else:
            results['std_miles'] = int((results['avg_miles'])/10)

        print('Final std ', int(results['std_true_price']))
        returnObject = {                'make': str(results.iloc[0]['make']),
                                        'model':str(results.iloc[0]['model']),
                                        'trim': str(results.iloc[0]['trim']),
                                        'Avg Price' : int(results['avg_true_price']),
                                        'Avg Mile' : int(results['avg_miles']),
                                        'Std Price' : int(results['std_true_price']),
                                        'Std Mile' : int(results['std_miles']),
                                        'count': int(results['count'])
                        }
        return returnObject

    #09
    def getCarInfoByMMT(self, make,model,trim):
        sql = '''
                SELECT 
                    max(distinct(upc_product_code)) as 'VIN', count(distinct(upc_product_code)) as 'total cars'
                FROM 
                    scrapeData_
                WHERE
                    make='{}' and model='{}' and trim = '{}'
                    '''.format(make,model,trim)

        results = pd.read_sql_query(sql, self.myDB)

        resultDict = {
                        "success": True, 
                        "VIN": results['VIN'],  
                        "data":results["total cars"]
                    }
                    
        return resultDict


    #10
    def getAutoMarketValue(self,vin):
            sql = '''
                    SELECT 
                        *
                    FROM 
                        tbl_market_value
                    WHERE
                    vin = '{}'
                        '''.format(vin)
            results = pd.read_sql_query(sql, self.myDB)
            resultDict = {}
            if results.empty :
                resultDict['success'] = False
            else:
                resultDict = {
                        "success": True,
                        "certainty": results.iloc[0]['certainty'],
                        "count": 58,
                        "mean": results.iloc[0]['mean'],
                        "mileage": results.iloc[0]['miles'],
                        "period": [
                            "2020-05-07",
                            "2020-10-26"
                        ],
                        "prices": {
                            "above": results.iloc[0]['price_above'],
                            "average": results.iloc[0]['price_average'],
                            "below": results.iloc[0]['price_below']
                        },
                        "stdev": results.iloc[0]['stdev'],
                        "vehicle": results.iloc[0]['vehicle'],
                        "vin": vin}
            return resultDict
    
    def savePredictedPrice(self,vin,miles,avg_price,above_price,below_price,trim,year,model,make,zip_code):
            added = datetime.date(datetime.now())
            sql =   '''
                    insert into tbl_predict_price (vin,miles,avg_price,above_price,below_price,trim,year,model,make,zip_code,added) 
                    values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}','{}',{},{})
                    '''.format(vin,miles,avg_price,above_price,below_price,trim,year,model,make,zip_code,added)
            try:    
                self.cHandler.execute(sql)
                #self.run_query(sql)   
            except Exception as e: 
                print("database error: " , e)



    #11
    def CheckPredictionHistory (self, upc_product_code,miles):
        sql= '''SELECT *,count(avg_price) as repeated
                FROM     tbl_predict_price
                WHERE vin='{}' and miles='{}' 
                GROUP BY avg_price
                ORDER BY repeated DESC
                LIMIT    1
        '''.format(str(upc_product_code),str(miles))
        results = pd.read_sql_query(sql, self.myDB)
        resultDict = {'make': str(results.iloc[0]['make']),
                        'model':str(results.iloc[0]['model']),
                        'trim': str(results.iloc[0]['trim']),
                        "avg_price": int(results['avg_price']),
                        "abv_price": int(results['above_price']),
                        "blw_price": int(results['below_price']),
                        "repeat" : int(results['repeated'])
                        }
        print("found in db (Prediction History) "+str(resultDict))
        return resultDict
    
    #12 Third party
    def auto_market_value(self,summarizedvalues):
            
            try:
                try:
                    key     = str(request.form['key'])
                except:
                    key     = '0BY2VDKPO9RUND'
                try:
                    VIN     = str(request.form['VIN'])
                except:
                    VIN     = summarizedvalues['upc_product_code']
                try:
                    mileage = int(request.form['mileage'])
                except:
                    mileage = int(request.form['miles'])
                try:
                    period  = int(request.form['period'])
                except:
                    period  = 180

                url = 'http://marketvalue.vinaudit.com/getmarketvalue.php?key={}&format=json&period={}&mileage={}&vin={}'.format(key,period,mileage,VIN,)
            except:
                return ("Feed input in correct form")

            try:
                    ldata = DBConnect().getAutoMarketValue(VIN)
                    print("from local database")
                    res = make_response(jsonify({"data": ldata}), 200)
                    return res
            except:
                    print("Trying to connect VIN audit")
                    resp = request.get(url)
            
            try:
                
                if(resp.json()['success']):
                    ldata = resp.json()
                    print("got from Third Party")
                    res = make_response(jsonify({"data": ldata}), 200)
                    return res
                else:
                    return res
            except:
                return("Error in code")

    #13 Extra Parmaeters
    def humancogn(self,summarizedvalues,seller_urgency=False ,inventory_level=False ,time_decay = False , competition_listings=False , historical_sales= True , 
                        market_data= False , product_features=False , offer_statistics=False, user_analytics=False, third_party=False,overall_condition=False):
    
        ''' 
            0) summarizedvalues is the set of summarizedprice & stats which needs to go through this parameters
            1) seller_urgency is Seller’s urgency
                    Explanation :	Enabling this feature means that the seller is in dire urgency to sell his car so we assure him with the lowest price that we commit to selling the car for within the next 45 days
                    Dependencies:   Std dev
                    Impact      :   -15% flat on both price   This should 
            
            2) inventory_level is Inventory level
                    Explanation :	Number of already available cars in our marketplace (TSR) for sale will decrease the chances of selling, so the price has to be low for registering newer i.e. S34
                    Dependencies:   TSR se transaction_type = seller ki counts 
                    Impact      :   -only[0-10%,] on both price            THis includes ki inventory m nhi hai toh both price bdha do 
            3) time_decay is Age of inventory or time decay
                    Explanation :	Once a new registered car then days passed till current date will impact the value of 
                    Dependencies:   TSR Table se added_on & expiry_date 
                    Impact      :   -only[0-10%,] on BuyerAsked only             #can be said as after 45 days its urgent to push it off

            4) competition_listings is Competition listings # FILTER with ZIP for both 
                    Explanation :	Number of already available cars in competetion marketplace for sale will, decrease the chances of selling, so the price has to be low for registering newer i.e. S34
                    Dependencies:   Counts for each website but for now [0,1] via tbl_all_cars
                    Impact      :   +-[0-10%,] on both                  THis includes ki competetion m km hai koi model  usuals se toh both price bdha do jaise BMW
                    
            5) historical_sales is Historical sales price
                    Explanation :	Past sales data will give us confidence in more of similar transaction thus will impact all 4 values
                    Dependencies:   Last transaction minus current date is dividing factor ...Least price sold and highest price bought should be consider via Closed deals API
                    Impact      :   +only[0-5-10%,] on both           Here we can make margin by not not changing selleraskedvalue          

            6) market_data is Market data API : Integration is done via VINaudit API impacting Buyer price by coming in mid

            7) product_features is Product features like AutoDriving, parking, GPS feature etc, Specialization is needed 

            8) offer_statistics is Buyer’s/Bidders response (offers)
                    Explanation :	Offered received for a car within a divided by timeframe, demand density, will increase both
                    Dependencies:   demand density, offered prices via All offers API
                    Impact      :   +only[0-10%,] on both           Here we can make margin by not not changing selleraskedvalue

            9) user_analytics is User's analytics and interests measure
                    Explanation :	Google analytics values like bounce rate,time spent, clicked thorugh, navigation time in exploring
                    Dependencies:   Analytics

            10)third_party is Actual sales Data API to be purchased
                    Explanation :	How third party are selling
                    Dependencies:   [-2,-1,0,1,2]

            11)overall_condition Condition (New vs Accidental) Specialization & discussion is needed
                    Explanation :	
                    Dependencies:   [-2,-1,0,1,2]


            returns summarizedprices[BuyerAskedPrice,SellerAskedPrice]
        '''
        considerations = []     #list of factors considered
        #1  seller_urgency

            # '''
            #             Least values  m se 1.5 time std minus krdo
            #             Impact S1234
            # '''
        impactfactors = {'1':1.5 , '2':1.25 , '3':0.5 , '4':-1 , '5':-1.5 , '1':-1 , '2':-1.5}

        factor = 1.5
        if seller_urgency :
            considerations.append("seller_urgency considered ")
            print("seller_urgency considered with factor", factor)
            try:
                    summarizedvalues['BuyerAskedPrice'] =  [[ summarizedvalues['BuyerAskedPrice'][0]   -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1]  - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                    summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0] -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1] - factor  *  summarizedvalues['stats']['Std Price'] ] ]
            except:
                    summarizedvalues['BuyerAskedPrice'] =  [[ summarizedvalues['BuyerAskedPrice'][0][0]   -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1][0]  - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                    summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0][0] -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1][0] - factor  *  summarizedvalues['stats']['Std Price'] ] ]
        else:
            print("seller_urgency not considered")




        #2  inventory_level
            # '''
            #             Z-score nikalo 'count' from tbl_all_cars, for [-2,-1,0,1,2] values 1.5 std max values +- krdo
            #             Impact S1234
            # '''
        if inventory_level :
            # GET TSR Dataframe se (mathced Quantity- TCD se sold Quantity) divided by (TSR )
            TSR =  self.getTSR(str(request.form['VIN']))
            TCD =  self.getTCD(str(request.form['VIN']))
            avail_inventory = len(TSR)
            sold_inventory  = len(TCD)

            try:
                factor = (avail_inventory-sold_inventory)/avail_inventory
            except:
                factor = 0

            considerations.append("inventory_level considered ")
            print("inventory_level considered with factor", factor)
            try:
                    summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0]   -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1]  - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                    summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0] -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1] - factor  *  summarizedvalues['stats']['Std Price'] ] ]
            except:
                    summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0][0]   -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1][0]  - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                    summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0][0] -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1][0] - factor  *  summarizedvalues['stats']['Std Price'] ] ]
        else:
            print("inventory_level not considered")

            

        #3  time_decay
            # '''
            #             In TSR Table, the added_on & expiry_date divided by current date & added on into 1.5std 
            #             Impact S1234
            # '''
        
        if time_decay :
            
            TSR                 = self.getTSR(str(request.form['VIN']))
            added_on            = TSR['added_on'][0]
            added_datetime      = datetime.strptime(str(added_on), '%Y-%m-%d %H:%M:%S')
            print(added_on)

            try:
                expiry_date     = time_decay   #Can be taken as input
                expiry_datetime = datetime.strptime(str(expiry_date), '%Y-%m-%d %H:%M:%S')
            except:
                expiry_date     = TSR['expiry_date'][0]   #Can be taken as input
                expiry_datetime = datetime.strptime(str(expiry_date), '%Y-%m-%d %H:%M:%S')
            print(expiry_date)


            current_date    = str(datetime.now()) #it should match with database timestamp
            current_datetime= datetime.strptime(str(current_date), '%Y-%m-%d %H:%M:%S.%f')
            print(current_date)

            # print('Date:', added_on.date())
            # print('Time:', added_on.time())
            # print('Date-time:', added_on)    

            # Age
            total_age       = (expiry_datetime -added_datetime).days 
            current_age     = (current_datetime-added_datetime).days
            print(total_age,current_age)
            
            if total_age < 0 or current_age < 0:
                    print ( "DateTime error.. Negative differnce calculated , hence time_decay factor not considered")
            elif    (current_age/total_age) >1:
                    factor = 1
                    considerations.append("time_decay considered ")
                    print ("time_decay factor is  considered with factor ", factor," but the product is expired, no more consideration of it henceforth")
                    try:
                            summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0]   -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1]  - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                            #summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0] -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1] - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                    except:
                            summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0][0]   -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1][0]  - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                            #summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0][0] -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1][0] - factor  *  summarizedvalues['stats']['Std Price'] ] ]
            else:
                    factor   = (current_age/total_age)  
                    considerations.append("time_decay considered ")
                    print("time_decay considered with factor", factor)
                    try:
                            summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0]   -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1]  - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                            #summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0] -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1] - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                    except:
                            summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0][0]   -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1][0]  - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                            #summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0][0] -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1][0] - factor  *  summarizedvalues['stats']['Std Price'] ] ]
            
        else:
            print("time_decay not considered")
            
        #4  competition_listings
            # '''
            #             Z-score nikalo 'count' from tbl_all_cars values std max values +- krdo
            #             Impact S1234
            # '''
        if competition_listings :
            try:
                sql = '''
                            SELECT 
                            avg(count) as avgcounts ,std(count) as stdcounts
                            FROM 
                            tbl_all_cars
                    '''
                
                results   = pd.read_sql_query(sql, self.myDB)
                avgcounts = int(results['avgcounts'])
                stdcounts = int(results['stdcounts'])
                counts    = int(summarizedvalues['stats']['count'])

                z_score   = (counts-avgcounts)/stdcounts        #statistical z score
                from math import e
                tanh      = 1 / (1+e**(-z_score))               #Activation function z score
                factor    = (2*tanh)-1
                considerations.append("competition_listings considered ")
                print("competition_listings considered with factor", factor)
                try:
                    summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0]   -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1]  - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                    summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0] -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1] - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                except:
                    summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0][0]   -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1][0]  - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                    summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0][0] -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1][0] - factor  *  summarizedvalues['stats']['Std Price'] ] ]
            except:
                print("competition_listings not considered something went wrong")
        else:
            print("competition_listings not considered")
        
        ###########
        #5  historical_sales
            # '''
            #             tbl_closed deals m se least and max.. see if there's any API
            #             + std / (max date of last closed deals =  last transaction on) minus current date
            #               Impact S1234
            # '''
        # try:
        if historical_sales:
                #max date of last closed deals can be input
                results =  self.getTCD(str(request.form['VIN']))
                
                # sellermax,sellermin   = results['type1_initial_offer'].median(),results['type1_negotiation_best_offer'].median()
                # buyermax,buyermin     = results['type2_initial_offer'].median(),results['type2_negotiation_best_offer'].median()
                
                # finalmedian = results['final_amount'].median()
                # finalmode   = results['final_amount'].mode()
                # finalmean   = results['final_amount'].mean()

                last_transaction = max(results['created_at'])
                current_date     = datetime.now()
                recent           = (current_date-last_transaction).days
                if recent==0:
                    recent=1
                if len(results)!=0:
                    factor       = len(results)/((len(results))+ (len(results)/recent))
                    if factor < 0:
                            print ( "DateTime error.. Negative differnce calculated , hence historical_sales not considered")
                    else:
                        considerations.append("historical_sales considered ")
                        print("historical_sales considered with factor", factor)
                        try:
                            summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0]   +  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1]  + factor  *  summarizedvalues['stats']['Std Price'] ] ]
                            summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0] +  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1] + factor  *  summarizedvalues['stats']['Std Price'] ] ]
                        except:
                            summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0][0]   +  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1][0]  + factor  *  summarizedvalues['stats']['Std Price'] ] ]
                            summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0][0] +  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1][0] + factor  *  summarizedvalues['stats']['Std Price'] ] ]
        else:
                print("historical_sales not considered") 
        # except:
                # print("historical_sales not considered something went wrong")

        ###########
        #6  market_data
            # '''
            #             Mid value of market and your predicted
            #             Impact B+12
            # '''
        if market_data:
            try:
                market_data     = DBConnect().auto_market_value(summarizedvalues)
                above,below,average= market_data['prices']['above'],market_data['prices']['below'],market_data['prices']['average']
                if above & below & average > 0 :    
                    summarizedvalues['BuyerAskedPrice'] = [ (summarizedvalues['BuyerAskedPrice'][0] +  below)/2,( summarizedvalues['BuyerAskedPrice'][1]  +  above)/2 ]
                    print("market_data considered")
                else:
                    print(" absurd market_data received hence not considered")
            except:
                    print("market_data not considered something went wrong")
        else:
                    print("market_data not considered")
        ###########
        #7  product_features
            # '''
            #             Product features like AutoDriving, parking, GPS feature etc, Specialization is needed 
            #             Impact S1234
            # '''

        impactfactors = {'-2':1.5 , '-1':1 , '0':0.5 , '+1':-1 , '+2':-1.5 , '1':-1 , '2':-1.5}

        if str(product_features) in  impactfactors.keys() :    
            factor = impactfactors[str(product_features)]
            considerations.append("product_features considered ")
            print("product_features considered with factor", factor)
            try:
                summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0]   -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1]  - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0] -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1] - factor  *  summarizedvalues['stats']['Std Price'] ] ]
            except:
                summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0][0]   -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1][0]  - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0][0] -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1][0] - factor  *  summarizedvalues['stats']['Std Price'] ] ]
        elif product_features == None:
            print("product_features not considered")
        else:
            print("Absurd value passed, try -2 to +2 values, product_features not considered")

        
        ###########
        #8  offer_statistics
            # '''
            #             Offered received for a car within a divided by timeframe, demand density, will increase the the SP and reduce CP
            #             Impact S1234
            # '''

        try:
            if offer_statistics :
                results =  self.getTSR(str(request.form['VIN']))
                #this can be feed manually
                totaloffers      =  len(results)
                timeframe        = (max(results['added_on']) - min(results['added_on'])).days
                demand_density   = totaloffers/(totaloffers+timeframe)
                #total_age       = (expiry_datetime -added_datetime).total_seconds() 
                #current_age     = (current_datetime-added_datetime).total_seconds()
                factor           = demand_density   #one and half time std 
                considerations.append("offer_statistics considered ")
                print("offer_statistics considered with factor", factor)
                try:
                    summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0]   +  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1]  + factor  *  summarizedvalues['stats']['Std Price'] ] ]
                    summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0] +  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1] + factor  *  summarizedvalues['stats']['Std Price'] ] ]
                except:
                    summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0][0]   +  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1][0]  + factor  *  summarizedvalues['stats']['Std Price'] ] ]
                    summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0][0] +  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1][0] + factor  *  summarizedvalues['stats']['Std Price'] ] ]

            else:
                print("offer_statistics not considered something went wrong ")
        except:
            print("offer_statistics not considered")

        #9  user_analytics
            # '''
            #             Analytics aajaye
            #             Impact S1234
            # '''
        impactfactors = {'-2':1.5 , '-1':1 , '0':0.5 , '+1':-1 , '+2':-1.5 , '1':-1 , '2':-1.5}

        if str(user_analytics) in  impactfactors.keys() :    
            factor = impactfactors[str(user_analytics)]
            try:
                summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0]   -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1]  - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0] -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1] - factor  *  summarizedvalues['stats']['Std Price'] ] ]
            except:
                summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0][0]   -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1][0]  - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0][0] -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1][0] - factor  *  summarizedvalues['stats']['Std Price'] ] ]
            considerations.append("user_analytics considered ")
            print("user_analytics considered with factor", factor)
        elif user_analytics == None:
            print("user_analytics not considered")
        else:
            print("Absurd value passed, try -2 to +2 values, user_analytics not considered")

        #10  third_party
            # '''
            #             Actual sales Data API to be purchased
            #             Impact S1234
            # '''
        impactfactors = {'-2':1.5 , '-1':1 , '0':0.5 ,'-0':-0.5 , '+1':-1 , '+2':-1.5 , '1':-1 , '2':-1.5}

        if str(third_party) in  impactfactors.keys() :    
            factor = impactfactors[str(third_party)]
            try:
                summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0]   -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1]  - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0] -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1] - factor  *  summarizedvalues['stats']['Std Price'] ] ]
            except:
                summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0][0]   -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1][0]  - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0][0] -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1][0] - factor  *  summarizedvalues['stats']['Std Price'] ] ]
            considerations.append("third_party considered ")
            print("third_party considered with factor", factor)
        elif third_party == None:
            print("third_party not considered")
        else:
            print("Absurd value passed, try -2 to +2 values, third_party not considered")

        


        #11  overall_condition
            # '''
            #             for [-2,-1,0,1,2] values 1.5 std max values +- krdo
            #             Impact S1234
            # '''

        impactfactors = {'-2':1.5 , '-1':1 , '0':0.5 , '-0':-0.5, '+1':-1 , '+2':-1.5 , '1':-1 , '2':-1.5}
        # try :
        if str(overall_condition) in  impactfactors.keys() :   
            factor  = impactfactors[str(overall_condition)]
            considerations.append("overall_condition considered ")
            print("overall_condition considered with factor", factor)
        
            try:
                summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0]   -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1]  - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0] -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1] - factor  *  summarizedvalues['stats']['Std Price'] ] ]
            except:
                summarizedvalues['BuyerAskedPrice']=  [[ summarizedvalues['BuyerAskedPrice'][0][0]   -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['BuyerAskedPrice'][1][0]  - factor  *  summarizedvalues['stats']['Std Price'] ] ]
                summarizedvalues['SellerAskedPrice']=  [[ summarizedvalues['SellerAskedPrice'][0][0] -  factor  *  summarizedvalues['stats']['Std Price'] ],[ summarizedvalues['SellerAskedPrice'][1][0] - factor  *  summarizedvalues['stats']['Std Price'] ] ]
        else:
            factor = 0
            print("overall_condition not considered")

        
        
        summarizedpriceANDstatus  = (summarizedvalues['BuyerAskedPrice'], summarizedvalues['SellerAskedPrice'],considerations)
        
        return summarizedpriceANDstatus









    def query(self, sql_statement):
        sql = sql_statement

        results = pd.read_sql_query(sql, self.myDB)

        return results

    #001
    def checkApiValidity(self,api_password):
        sql = '''
        select count(api_password) as count from tbl_clients where api_password = '{}'
        '''.format(api_password)
        try:
            result = self.query(sql) 
            if result.loc[0]['count'] > 0:
                return True
            return False
        except: 
            return False