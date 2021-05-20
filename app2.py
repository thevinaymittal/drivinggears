from flask import *
import json
import time
import pandas as pd
import requests
from Database.db import DBConnect
from Database.iadb import DBConnect168
import numpy as np
import logging
from datetime import datetime
from flasgger import Swagger
import numpy as np
import pickle
import pandas as pd
from flask import Flask, abort, jsonify, request
from iautils import convertJsonObjectToNameSpace as convertJOtoNS
from models.AutoMarketValue import AutoMarketValue
from flask_cors import CORS, cross_origin
mlModel = pickle.load(open("Decision_Trees.pkl", "rb"))         #Trained AI ML model from 10 Million of scrapped data
encoded = pickle.load(open("OrdinalEncoder.pkl", "rb"))         #This will make sure that the data which you gonna input is cleaned enough to predict



app = Flask(__name__)
app.secret_key = "super secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
Swagger(app)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

CORS(app, support_credentials=True, origin='*')
@cross_origin(supports_credentials=True)


# Route 00
@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")


# Route 00
@app.route('/prediction', methods=['GET', 'POST'])
def price_predic():
    if(request.method != 'POST'):
        return render_template('predict_price.html')
    else: 
        dbc = DBConnect()
        req = request.get_json()
        print(req)
        if not dbc.checkApiValidity(req['api_password']):
            return {"success": True, "error": "api is invalid, please contact support team!"}
        res = make_response(jResult, 200)
        return res

# Route 00
@app.route('/scrapped', methods=['GET', 'POST'])
def price_status():
    if(request.method != 'POST'):
        return render_template('price_status.html')
    else: 
        req = request.get_json()
        print(req)
        dbc = DBConnect()
        try:
            if not dbc.checkApiValidity(req['api_password']):
                return {"success": True, "error": "api is invalid, please contact support team!"}
            jResult = dbc.getCarInfoByVin(req['vin'])
            print(jResult)
            res = make_response(jResult, 200)
            return res
        except:
            print("Service Unavailable now")
            return ({"Service Unavailable now":"Service Unavailable now"})
        

# Route 00
@app.route('/NHTSA', methods=['POST','GET'])
def car_search():
    if(request.method != 'POST'):
    
        return render_template('car_info.html')
    else:
        req = request.get_json()
        print(req)
        dbc = DBConnect()
        if not dbc.checkApiValidity(req['api_password']):
            return {"success": True, "error": "api is invalid, please contact support team!"}

        vin_search_url = 'https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{}?format=json'.format(req['vin'])
        resp = requests.get(vin_search_url)
        res = make_response(jsonify({"data": resp.json()}), 200)
        return res


# Route 01
@app.route('/vinaudit', methods=['POST','GET'])
def auto_market_value():
    if(request.method != 'POST'):
        return render_template('marketvalue.html')
    else:
        dbc = DBConnect()
        if not dbc.checkApiValidity(request.form['api_password']):
            return {"success": True, "error": "api is invalid, please contact support team!"}
        if(request.form.get('key')):
            try:
                key     = str(request.form['key'])
                VIN     = str(request.form['VIN'])
                vin     = VIN
                mileage = int(request.form['mileage'])
                period  = int(request.form['period'])
                url = 'http://marketvalue.vinaudit.com/getmarketvalue.php?key={}&format=json&period={}&mileage={}&vin={}'.format(key,period,mileage,VIN,)
            except:
                return ("Feed input in correct form")

            try:
                    ldata = DBConnect().getAutoMarketValue(VIN)
                    print("from local database")
                    res = make_response(jsonify({"data": ldata}), 200)
                    return res
            except:
                    print("Trying to connecr VIN audit")
                    resp = requests.get(url)
            
            try:
                
                if(resp.json()['success']):
                    saveVinAuditSearchDb209(resp)
                    # saveVinAuditSearchDb168(resp)
                    print('saved...')
                    ldata = resp.json()
                    print("got from server")
                    res = make_response(jsonify({"data": ldata}), 200)
                    return res
                else:
                    return res
            except:
                return("Error in code")
        else:
            return ("Please enter the Key")


def saveVinAuditSearchDb209(resp):
        dbc = DBConnect()
        mv= AutoMarketValue(convertJOtoNS(json.dumps(resp.json())))
        dbc.saveAutoMarketValueSearch(mv.vin,mv.miles,mv.vehicle,mv.price_average,mv.price_below,mv.price_above, mv.centainty,mv.mean,mv.stdev)
def saveVinAuditSearchDb168(resp):
        dbc = DBConnect168()
        mv= AutoMarketValue(convertJOtoNS(json.dumps(resp.json())))
        dbc.saveAutoMarketValueSearch(mv.vin,mv.miles,mv.vehicle,mv.price_average,mv.price_below,mv.price_above, mv.centainty,mv.mean,mv.stdev)

def savePredictPriceDb168(form,pprice):
        
        #We want to save make model trim from calculating not from form submission
        #also since this calculation is already done in prediction function 
        #how can we fetch this make model trim from there

        upc_product_code = str(request.form['VIN'])
        VINcode = upc_product_code[:8]
        msgVIN  = DBConnect().checkVIN(str(VINcode))
        make  = msgVIN['make']
        model = msgVIN['model'] 
        trim  = msgVIN['trim']

        
        DBConnect168().savePredictedPrice(
            form.get('VIN'),
            form.get('miles'),
            pprice.get('average_price').get("value"),
            pprice.get('above_market_price').get("value"),
            pprice.get('below_market_price').get("value"),
            trim,
            form.get('year'),
            model,
            make,
            form.get('zip_code')
        )
        
def savePredictPriceDb209(form,pprice):
        DBConnect().savePredictedPrice(
        form.get('VIN'),
        form.get('miles'),
        pprice.get('average_price').get("value"),
        pprice.get('above_market_price').get("value"),
        pprice.get('below_market_price').get("value"),
        form.get('trim'),
        form.get('year'),
        form.get('model'),
        form.get('make'),
        form.get('zip_code'),
        )
        pass

#Route 2
@app.route('/predict', methods=['POST'])
def getPredictedPrice():
    '''
    param  : make,model,trim,year,miles,zip_code, VIN(optional)
    return : predicted price of car as per input params
    '''
        
    connection = DBConnect()
    print(datetime.now())
    if not connection.checkApiValidity(request.form['api_password']):
            return {"success": True, "error": "api is invalid, please contact support team!"}
    
    if request.form.get('miles'):
            print(request.form)
            #1
            try:
                miles = int(request.form['miles'])
                assert miles>=0 , EOFError 

            except:
                msg = {"'Invalid 'Miles' value, please try with any positive integer'":'Failed'}
                return msg, 500

            #2
            try:
                zip_code = int(request.form['zip_code'])
                locate = connection.checkZip(int(zip_code))
                city   = locate['city']
                county = locate['county']
                state  = locate['state']
            except:
                msg = {"Invalid 'Zip' value, please try with standard Zip Codes available in USA":"Failed"}
                return msg, 500
            
            #3
            try:
                        year = int(request.form['year'])
                        connection.checkYear(int(year))
            except:
                        msg = {"'Invalid 'Year' value, please try from 1997 till 2020'":'Failed'}
                        return msg, 500 

            #4
            if request.form.get('VIN'):

                try:
                    upc_product_code = str(request.form['VIN'])
                    result = connection.CheckPredictionHistory(str(upc_product_code),int(miles))
                    Avgmarket= int(result['avg_price'])
                    Bmarket  = int(result['blw_price'])
                    Amarket  = int(result['abv_price'])
                    make     = result['make']
                    model    = result['model']
                    trim     = result['trim']

                    print("Predicting from database "+str(len(result)))
                
                except:
                
                        try:
                                
                                upc_product_code = str(request.form['VIN'])             #VIN is fetched in form 
                                VINcode = upc_product_code[:8]
                                print('Second', datetime.now())
                                results  = connection.getAvgStd(str(VINcode))
                                print("VIN accepted  " + str(upc_product_code))
                                
                                make  = str(results['make'])
                                model = str(results['model'])
                                trim  = str(results['trim'])
                                mileages= int(miles)
                                Avg_Price   = int(results['Avg Price'])
                                Std_Price   = int(results['Std Price'])
                                
                                print(datetime.now())
                                #1
                                
                                print('good input had')

                                try:
                                    #2
                                    prediction=0
                                    
                                    while prediction<=0:
                                        input_data=[[make,model,str(trim),year,mileages,zip_code]]
                                        df=pd.DataFrame(input_data)
                                        df[[0,1,2]]=encoded.transform(df[[0,1,2]])
                                        feed_data=df
                                        print('better encoded.. now trying')

                                        #3
                                        u_pred=mlModel.predict(feed_data)                   # Here's where AI will be predicting one price point for a given car 
                                        u_list=u_pred.tolist()                              # we took the data points needed in prediction earlier only before this line 
                                        prediction=float(u_list[0])
                                        mileages=int(mileages*0.8)
                                    print('best prediction made')
                                    print(prediction)
                                    #4
                                    print(datetime.now())
                                    print("Getting avg  " + str(VINcode))
                                    
                                    if ((Avg_Price/20) > Std_Price):
                                        Bmarket  = int(int(prediction) - 2*int(results['Std Price']))
                                        Amarket  = int(prediction) 
                                        Avgmarket= int(prediction)     - int(results['Std Price'])
                                    else :
                                        
                                        Bmarket  = int(int(prediction) - 2*int(results['Std Price']))
                                        Amarket  = int(prediction) - 1.25*int(results['Std Price'])
                                        Avgmarket= int(prediction)     - 1.75*int(results['Std Price'])
                                    print(datetime.now())
                                    #5
                                    print("caching")
                                    
                                    # DBConnect168().savePredictedPrice(
                                    # vin=upc_product_code,
                                    # miles=miles,
                                    # avg_price= Avgmarket,
                                    # above_price= Amarket,
                                    # below_price= Bmarket,
                                    # trim=trim,
                                    # year=year,
                                    # model=model,
                                    # make=make,
                                    # zip_code=zip_code
                                    # )
                                    # print('caching more')

                                    DBConnect().savePredictedPrice(
                                    vin=upc_product_code,
                                    miles=miles,
                                    avg_price= Avgmarket,
                                    above_price= Amarket,
                                    below_price= Bmarket,
                                    trim=trim,
                                    year=year,
                                    model=model,
                                    make=make,
                                    zip_code=zip_code
                                    )

                                    
                                except:
                                    return ('avg fetched error')





                        except:
                                msg = {"Invalid 'VIN' value, please try with standard VIN number":'Failed'}
                                return msg, 500
                
                
            else:

                    #3
                    try:
                        make = (request.form['make'])
                        #Condition to verify this from scrapeData_ table 'make' column
                    except:
                        msg = {"'Invalid 'Make' value, Check case sensitive or please try with any standard Car Makers available in USA'":'Failed'}
                        return msg, 500
                    #4
                    try:
                        model = (request.form['model'])
                        #Condition to verify this from scrapeData_ table 'model' column
                    except:
                        msg = {"'Invalid 'Model' value, Check case sensitive or please try with the available Models under the Maker available in USA'":'Failed'}
                        return msg, 500
                    
                    #5
                    try:
                        trim = (request.form['trim'])
                        #Condition to verify this from scrapeData_ table 'trim' column
                    except:
                        msg = {"'Invalid 'Trim' value, Check case sensitive or please try with the available Trim/Variant under the Models available in USA'":'Failed'}
                        return msg, 500
                    
                    try:
                        upc = connection.getCarInfoByMMT(make,model,str(trim))
                        upc_product_code = upc['VIN']
                        VINcode=upc_product_code[:8]
                        assert (len(upc_product_code) <= 16 and len(upc_product_code) >= 8 )
                    except:
                        return("Sorry VIN can not be retrieved please feed manually")
            

            

                
            try:
                print("printing started")    
                print(datetime.now())
                jBmarket = {
                    "value": Bmarket,
                    "label": "has the lowest market trend value from $",
                }
                jAvgmarket = {
                    "value": Avgmarket,
                    "label": "similiar cars which made transaction are",
                }
                jAmarket = {
                    "value": Amarket,
                    "label": "upto the highest market trend value $",
                }
                jIn = {
                    "value": "{} {} {}".format(city,state,county),
                    "label": "in",
                    }
                
                jMiles = {
                    "value": miles,
                    "label": "covering miles",
                    }
                print("in make model")
                jCar = {
                    "value": "{} {} {}".format(make,model,trim),
                    "label": "For the car "
                }
                predDict = {"success": True,
                            "below_market_price":jBmarket,
                            "above_market_price":jAmarket, 
                            "average_price":jAvgmarket, 
                            "in": jIn, 
                            "miles": jMiles,
                            "car":jCar
                            }
                print(datetime.now())
                
                return predDict,200
                

            except:
                msg = {'success': False,'something is printing':'please check'}
                return msg, 500
    else:
            msg = {'success': False,'something is wrong in connection 2':'Use post method'}
            return msg, 500



#Route 3
@app.route('/stats', methods=['POST'])
def Price():
    '''
    param  : make,model,trim,year or VIN(optional)
    return : average price with avg miles of car as per input params from scrapped data
    '''
    if request.method == 'POST':
        print(datetime.now())
        connection = DBConnect()
        if not connection.checkApiValidity(request.form['api_password']):
            return {"success": True, "error": "api is invalid, please contact support team!"}

        if request.form.get('VIN') :

                    try:
                        upc_product_code = str(request.form['VIN'])
                        VINcode = upc_product_code[:8]
                        statresults  = connection.getAvgStd(str(VINcode))
                        print(datetime.now())
                        print("VIN accepted  " + str(upc_product_code))
                        
                        make  = statresults['make']
                        model = statresults['model']
                        trim  = statresults['trim']

                        print("Getting avg for "+str(VINcode))
                        Avgmarket= int(statresults['Avg Price'])
                        Bmarket  = int(Avgmarket) - int(statresults['Std Price'])
                        Amarket  = int(Avgmarket) + int(statresults['Std Price'])
                        jBmarket = {
                            "value": Bmarket,
                            "label": "has the lowest market trend value from $",
                        }
                        jAvgmarket = {
                            "value": Avgmarket,
                            "label": "similiar cars which made transaction are",
                        }
                        jAmarket = {
                            "value": Amarket,
                            "label": "upto the highest market trend value $",
                        }
                        jAvgMiles = {
                            "value": int(statresults["Avg Mile"]),
                            "label": "and covered an average miles of ",
                        }
                        jCar = {
                            "value": "{} {} {}".format(make,model,trim),
                            "label": "For the car "
                        }
                        print(datetime.now())
                        print("printing")
                        statDict = {"success": True,
                                    "below_market_price":jBmarket,
                                    "above_market_price":jAmarket, 
                                    "average_price":jAvgmarket, 
                                    "average_miles": jAvgMiles,
                                    "car":jCar}
                        # = {"success": True,"Below Market trend $":Bmarket,"Above Market trend $":Amarket, "Average trend $":Avgmarket, "For the car ": "{} {} {}".format(make,model,trim), "at average miles of " : int(statresults["Avg Mile"]) }
                        return statDict,200 

                        
                    except:
                        msg = {"Invalid 'VIN' value, please try with a standard VIN number":'Failed'}
                        return msg, 500
            
        else:

                    #3
                    try:
                        make = (request.form['make'])
                        #Condition to verify this from scrapeData_ table 'make' column
                    except:
                        msg = {"'Invalid 'Make' value, Check case sensitive or please try with any standard Car Makers available in USA'":'Failed'}
                        return msg, 500

                    #4
                    try:
                        model = (request.form['model'])
                        #Condition to verify this from scrapeData_ table 'model' column
                    except:
                        msg = {"'Invalid 'Model' value, Check case sensitive or please try with the available Models under the Maker available in USA'":'Failed'}
                        return msg, 500
                    
                    #5
                    try:
                        trim = (request.form['trim'])
                        #Condition to verify this from scrapeData_ table 'trim' column
                    except:
                        msg = {"'Invalid 'Trim' value, Check case sensitive or please try with the available Trim/Variant under the Models available in USA'":'Failed'}
                        return msg, 500

                    #6 To deduce VIN from this make model trim
                    try:
                        VINdict = connection.getCarInfoByMMT(make,model,trim)
                        VINcode = str(VINdict['VIN'])
                        print("VIN deduced ")
                    except:
                        msg = {"'Invalid Make-Model_Trim values, Check case sensitive or please try with the available Trim/Variant under the Models available in USA'":'Failed'}
                        return msg, 500
        
    else:
            return {'success':False,"NO VIN found":"failed"}


#Route 4
@app.route('/summarized', methods=['POST'])
def getSummarizedPrice():
    '''
    param  : VIN, mileage
    return : Lowest and Highest value of the car from All three Values calulated above
    '''
    if request.method == 'POST':
        print(datetime.now())
        connection = DBConnect()
        # if not connection.checkApiValidity(request.form['api_password']):
            # return {"success": True, "error": "api is invalid, please contact support team!"}

        if request.form.get('VIN') :
            #00
                try:
                    try:
                        mileage = int(request.form['mileage'])
                    except:
                        mileage = int(request.form['miles'])
                        
                    assert mileage>=0 , EOFError
                    miles   = mileage 
                except:
                    return "mileage should be positive integer"

            #01
                try:
                    zip_code = int(request.form['zip_code'])
                    locate = connection.checkZip(int(zip_code))
                    city   = locate['city']
                    county = locate['county']
                    state  = locate['state']
                except:
                    msg = {"Invalid 'Zip' value, please try with standard Zip Codes available in USA":"Failed"}
                    return msg, 500

            #01 AI values
            
                try:
                    upc_product_code = str(request.form['VIN'])
                    result = connection.CheckPredictionHistory(str(upc_product_code),int(mileage))
                    AvgmarketofAI= int(result['avg_price'])
                    BmarketofAI  = int(result['blw_price'])
                    AmarketofAI  = int(result['abv_price'])
                    Avg_Price   = int(result['Avg Price'])
                    Std_Price   = int(result['Std Price'])
                    make     = result['make']
                    model    = result['model']
                    trim     = result['trim']

                    print("Predicting from database "+str(len(result)))
                
                except:
                
                    try:
                                print(datetime.now())
                                upc_product_code = str(request.form['VIN'])
                                VINcode = upc_product_code[:8]
                                results  = connection.getAvgStd(str(VINcode))
                                print("VIN accepted  " + str(upc_product_code))
                                
                                make  = str(results['make'])
                                model = str(results['model'])
                                trim  = str(results['trim'])
                                try:
                                    year  = str(request.form['year'])       #MAY BE ERROR
                                except:
                                    year  = 2020
                                mileages = int(miles)
                                Avg_Price   = int(results['Avg Price'])
                                Std_Price   = int(results['Std Price'])
                                # zip_code=94002
                                print(datetime.now())
                                #1
                                print('good input had')

                                try:
                                    #2
                                    prediction=0
                                    
                                    while prediction<=0:
                                        input_data=[[make,model,str(trim),year,mileages,zip_code]]
                                        df=pd.DataFrame(input_data)
                                        df[[0,1,2]]=encoded.transform(df[[0,1,2]])
                                        feed_data=df
                                        print('better encoded.. now trying')

                                        #3
                                        u_pred=mlModel.predict(feed_data)                   # Here's where AI will be predicting one price point for a given car 
                                        u_list=u_pred.tolist()                              # we took the data points needed in prediction earlier only before this line 
                                        
                                        prediction=float(u_list[0])
                                        mileages=int(int(mileages)*0.8)

                                    if Std_Price < int(prediction/10) :
                                        pass
                                    else:
                                        Std_Price = int(prediction/10)

                                    print('best prediction made')
                                    print(prediction)
                                    #4
                                    print(datetime.now())
                                    print("Getting avg  :" + str(Avg_Price)+ " with STD :"+str(Std_Price))
                                    
                                    # if ((Avg_Price/20) > Std_Price):
                                    #     BmarketofAI  = int(int(prediction) - 2*Std_Price)
                                    #     AmarketofAI  = int(prediction) 
                                    #     AvgmarketofAI= int(prediction)     - Std_Price
                                    # else :
                                        
                                    BmarketofAI  = int(int(prediction) - Std_Price)
                                    AmarketofAI  = int(prediction)     + Std_Price
                                    AvgmarketofAI= int(prediction)     
                                    print(datetime.now())
                                    #5
                                    print("caching")
                                    
                                    # DBConnect168().savePredictedPrice(
                                    # vin=upc_product_code,
                                    # miles=miles,
                                    # avg_price= Avgmarket,
                                    # above_price= Amarket,
                                    # below_price= Bmarket,
                                    # trim=trim,
                                    # year=year,
                                    # model=model,
                                    # make=make,
                                    # zip_code=zip_code
                                    # )
                                    # print('caching more')

                                    DBConnect().savePredictedPrice(
                                    vin=upc_product_code,
                                    miles=miles,
                                    avg_price= AvgmarketofAI,
                                    above_price= AmarketofAI,
                                    below_price= BmarketofAI,
                                    trim=trim,
                                    year=year,
                                    model=model,
                                    make=make,
                                    zip_code=zip_code
                                    )

                                    
                                except Exception as e:
                                    print(e)
                                    return ('Prediction fetched error')
                    except Exception as e:
                                print(e)
                                msg = {"Invalid values, please try with standard VIN number":'Failed'}
                                return msg, 500
                                
                #02 Stats

                try:
                        upc_product_code = str(request.form['VIN'])
                        VINcode = upc_product_code[:8]
                        statresults  = connection.getAvgStd(str(VINcode))
                        print(datetime.now())
                        print("VIN accepted  " + str(upc_product_code))
                        AvgmarketofStats= int(statresults['Avg Price'])
                        BmarketofStats  = int(AvgmarketofStats) - int(statresults['Std Price'])
                        AmarketofStats  = int(AvgmarketofStats) + int(statresults['Std Price'])
                except:
                    return("Stats not produced")
                #end of stats

                #03 VINaudit, simply copied the code from above
                dbc = DBConnect()
                if not dbc.checkApiValidity(request.form['api_password']):
                    return {"success": True, "error": "api is invalid, please contact support team!"}
                if(request.form.get('key')):
                    try:
                        key     = str(request.form['key'])
                        VIN     = str(request.form['VIN'])
                        # vin     = VIN
                        try:
                            mileage = int(request.form['mileage'])
                        except:
                            mileage = int(request.form['miles'])
                        period  = 180
                        url = 'http://marketvalue.vinaudit.com/getmarketvalue.php?key={}&format=json&period={}&mileage={}&vin={}'.format(key,period,mileage,VIN,)
                    except:
                        return ("Feed input in correct form")

                    try:
                            print("Trying from local database")
                            ldata = DBConnect().getAutoMarketValue(VIN)
                            print(ldata)
                            AmarketofVINaudit = ldata['prices']['above']
                            BmarketofVINaudit = ldata['prices']['below']
                            print(AmarketofVINaudit,BmarketofVINaudit)
                    except:
                        print("but VIN is missign so now Trying to connect VIN audit web")
                        resp = {}
                        try:
                            resp = requests.get(url)
                        except:
                            resp = None
                    
                        try:
                            #resp.json()['success']
                            if(resp and resp.json()['success']):
                                saveVinAuditSearchDb209(resp)
                                # saveVinAuditSearchDb168(resp)
                                print('saved...')
                                ldata = resp.json()
                                print(ldata)
                                AmarketofVINaudit = ldata['prices']['above']
                                BmarketofVINaudit = ldata['prices']['below']
                                print(AmarketofVINaudit,BmarketofVINaudit)
                                print("got from server")
                            else:
                                print("VINAudit fails")
                                print(BmarketofAI)
                                print(int(statresults['Std Price']))
                                
                                ldata = {
                                            "success": True,

                                            "prices": 
                                            {
                                                "above": AmarketofAI,
                                                "below": BmarketofAI
                                            },

                                            "stdev": int(statresults['Std Price'])
                                        }
                                print(ldata)
                                AmarketofVINaudit = ldata['prices']['above']
                                BmarketofVINaudit = ldata['prices']['below']
                                print(AmarketofVINaudit,BmarketofVINaudit)
                        except:
                            return("Error in code")
                else:
                    return ("Please enter the Key")
                                        

                
                #Finally return the range:
                #We are suggesting price for a car when a buyer or seller comes.. so buyer is projected higher of all three prices and seller is projected lower of all 3
                BBuyerAsked = max(AmarketofAI,AmarketofStats,int(float(AmarketofVINaudit))) -  int(Std_Price)
                ABuyerAsked = max(AmarketofAI,AmarketofStats,int(float(AmarketofVINaudit)))
                BSellerAsked= min(BmarketofAI,BmarketofStats,int(float(BmarketofVINaudit)))
                ASellerAsked= min(BmarketofAI,BmarketofStats,int(float(BmarketofVINaudit)))+  int(Std_Price)

                BBuyerAsked = min(AmarketofAI,AmarketofStats,int(float(AmarketofVINaudit))) -  int(Std_Price)
                ABuyerAsked = min(AmarketofAI,AmarketofStats,int(float(AmarketofVINaudit)))
                BSellerAsked= min(BmarketofAI,BmarketofStats,int(float(BmarketofVINaudit)))
                ASellerAsked= min(BmarketofAI,BmarketofStats,int(float(BmarketofVINaudit)))+  int(Std_Price)


                summarizedpricesold = [BBuyerAsked,ABuyerAsked,BSellerAsked,ASellerAsked]
                print("summarizedpricesold",summarizedpricesold)
                summarizedvalues= {"BuyerAskedPrice":[BBuyerAsked,ABuyerAsked],"SellerAskedPrice":[BSellerAsked,ASellerAsked],"stats" :statresults,"upc_product_code":upc_product_code}

                #time_decay can have expiry_date input
                #competition_listings can have [0,1]
                
                try:
                    seller_urgency,inventory_level,time_decay = request.form.get('seller_urgency'), request.form.get('inventory_level'), request.form.get('time_decay')
                    competition_listings, historical_sales    = request.form.get('competition_listings'), request.form.get('historical_sales')  
                    market_data, product_features             = request.form.get('market_data'), request.form.get('product_features')  
                    offer_statistics, user_analytics          = request.form.get('offer_statistics'), request.form.get('user_analytics')   
                    third_party,overall_condition             = request.form.get('third_party'), request.form.get('overall_condition') 
                    
                    # humanparams  = [seller_urgency,inventory_level,time_decay,competition_listings, historical_sales,market_data, product_features,offer_statistics, user_analytics,third_party,overall_condition]
                except:
                    pass
                try:

                    summarizedpriceANDstatus  = connection.humancogn(summarizedvalues,seller_urgency,inventory_level,time_decay,competition_listings, historical_sales,market_data, product_features,offer_statistics, user_analytics,third_party,overall_condition)
                    [[BBuyerAsked],[ABuyerAsked]] , [[BSellerAsked],[ASellerAsked]],considerations = summarizedpriceANDstatus
                    summarizedprices = [BBuyerAsked,ABuyerAsked,BSellerAsked,ASellerAsked]
                    return {"summarizedpricesold" : summarizedpricesold,"BuyerAskedPrice":[int(summarizedprices[0]),int(summarizedprices[1])],"SellerAskedPrice":[int(summarizedprices[2]),int(summarizedprices[3])],"zConsiderations :" : considerations, "a For ": "{} {} {}".format(city,state,county)}

                except:
                    return {"BuyerAskedPrice":[int(summarizedpricesold[0]),int(summarizedpricesold[1])],"SellerAskedPrice":[int(summarizedpricesold[2]),int(summarizedpricesold[3])],"a For ": "{} {} {}".format(city,state,county)}    
        
        
        else:
            return {'success':False,"NO VIN found":"failed"}
    else:
            return {'success':False,"Post method":"failed"}
    

if __name__ == '__main__':
    app.run(debug=True,port=8080)