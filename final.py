#importing dependencies
from flask import *
import io
import os
import time
import ast
import json
import pandas as pd
import sys
import numpy as np
import logging
from datetime import datetime
# from flask_restplus import Api, Resource, reqparse
from io import StringIO
#from flasgger import Swagger
import numpy as np
import pickle
import pandas as pd
import xgboost as xgb
from Database.db import DBConnect
from flask import Flask, abort, jsonify, request
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OrdinalEncoder


#importing trained models as a pickle
mlModel = pickle.load(open("Decision_Trees1.pkl", "rb"))
encoded = pickle.load(open("OrdinalEncoder.pkl", "rb"))
# fullyEncoded = pickle.load(open("Pickle_Sc_Model.pkl", "rb"))


#
app = Flask(__name__)

app.secret_key = "super secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

Swagger(app)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    application.logger.handlers = gunicorn_logger.handlers
    application.logger.setLevel(gunicorn_logger.level)
#



#Route 1
@app.route('/', methods=['GET'])
def index():
    '''
    param  : base url will be called as GET 
    return : "Flask is up"
    '''
    return "Prediction API is good to go"








#Route 2
@app.route('/api/predict', methods=['POST'])
def getPredictedPrice():
    '''
    param  : make,model,trim,year,miles,zip_code, VIN(optional)
    return : predicted price of car as per input params

    '''
    
    if request.method == 'POST':
        connection = DBConnect()
        if request.form.get('miles'):
            #1
            try:
                miles = int(request.form['miles'])
                connection.checkMiles(miles)

            except:
                msg = {"'Invalid 'Miles' value, please try with any positive integer'":'Failed'}
                # msg = {"fail":d.checkMiles(miles).msg}
                return msg, 500

            #2
            try:
                zip_code = int(request.form['zip_code'])
                msgZip = connection.checkZip(zip_code)

                #Condition to verify this from Truecar_ table
            except:
                msg = {"Invalid 'Zip' value, please try with standard Zip Codes available in USA":"Failed"}
                return msg, 500
            
            # 

            if request.form.get('VIN'):

                    try:
                        upc_product_code = str(request.form['VIN'])
                        VINcode = upc_product_code[:8]
                        msgVIN  = connection.checkVIN(str(VINcode))
                        print("VIN accepted  " + str(upc_product_code))
                        
                        make  = msgVIN['make']
                        model = msgVIN['model']
                        trim  = msgVIN['trim']
                        # return {"Hi":str(msg)}, 200
                        #Condition (i.e. run function name_from_VIN) to verify this from scrapeData_ table upc_product_code column and then feed:
                        # make,model,trim,year = db.name_from_VIN(upc_product_code)
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

            #6
            try:
                        year = int(request.form['year'])
                        connection.checkYear(int(year))
                        #Condition to verify this from scrapeData_ table 'year' column
            except:
                        msg = {"'Invalid 'Year' value, please try from 1997 till 2020'":'Failed'}
                        return msg, 500



            try:
                
                input_data=[[make,model,str(trim),year,int(miles),zip_code]]
                print('good')
                df=pd.DataFrame(input_data)
                df[[0,1,2]]=encoded.transform(df[[0,1,2]])
                feed_data=df
                # feed_data=fullyEncoded.transform(df)
                print('better')
                u_pred=mlModel.predict(feed_data)
                u_list=u_pred.tolist()
                print('best')
                # prediction ="HI"
                prediction=float(u_list[0])
                return {'Price Predicted for ':str(prediction)}
                # return {'Price Predicted for {} and {}'.format(msgVIN, msgZip) :str(prediction)}
                

            except:
                msg = {'something is wrong in connection':'sf'}
                return msg, 500
        else:
            pass
    else:
        pass



#Route 3
@app.route('/api/stats', methods=['POST'])
def getStatsPrice():
    '''
    param  : make,model,trim,year,miles,zip_code, VIN(optional)
    return : average price with avg miles of car as per input params
                from scrapped data
    '''
    if request.method == 'POST':
        connection = DBConnect()

        if request.form.get('miles'):
            #1
            try:
                miles = int(request.form['miles'])
                connection.checkMiles(miles)

            except:
                msg = {"'Invalid 'Miles' value, please try with any positive integer'":'Failed'}
                return msg, 500

            #2
            try:
                zip_code = int(request.form['zip_code'])
                msgZip = connection.checkZip(zip_code)

                #Condition to verify this from Truecar_ table
            except:
                msg = {"Invalid 'Zip' value, please try with standard Zip Codes available in USA":"Failed"}
                return msg, 500
            
            # 

            if request.form.get('VIN'):

                    try:
                        upc_product_code = str(request.form['VIN'])
                        VINcode = upc_product_code[:8]
                        msgVIN  = connection.checkVIN(str(VINcode))
                        print("VIN accepted  " + str(upc_product_code))
                        
                        make  = msgVIN['make']
                        model = msgVIN['model']
                        trim  = msgVIN['trim']
                        #Condition (i.e. run function name_from_VIN) to verify this from scrapeData_ table upc_product_code column and then feed:
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

            #6
            try:
                        year = int(request.form['year'])
                        connection.checkYear(int(year))
                        #Condition to verify this from scrapeData_ table 'year' column
            except:
                        msg = {"'Invalid 'Year' value, please try from 1997 till 2020'":'Failed'}
                        return msg, 500



            try:
                
                return connection.getStats()
                
            except:
                msg = {'something is wrong in scrapper':'sf'}
                return msg, 500
        else:
            pass
    else:
        pass



if __name__ == '__main__':
    # application.run(debug=True,port=80,host='0.0.0.0')
    app.run(debug=True)
