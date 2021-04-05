import pandas as pd
from flask import *
import pymysql
import datetime
from datetime import datetime
import time
import json
import config

def getSqlToPandas():
    return SqlToPandas()
class SqlToPandas():
    """docstring for DBConnect"""

    #def __init__(self):
        # self.myDB = pymysql.connect(host='209.126.3.200', port=int(3306), 
        #                 user='mi_user', passwd='ce251CwE584##878', 
        #                 db='mi_dbmark', autocommit=True)
        # self.DbConnectbeta= pymysql.connect(host='209.126.3.200', port=int(3306), 
        #                 user='beta_user', passwd='cEe8dcSSd84dHH012', 
        #                 db='beta_base', autocommit=True)
        # self.DbConnectapi=pymysql.connect(host='209.126.3.200', port=int(3306), 
        #                 user='api_user', passwd='RM1Z7HmKe2MVHH256', 
        #                 db='api_base', autocommit=True)
        # self.DbConnectdev6= pymysql.connect(host='209.126.3.200', port=int(3306), 
        #                 user='dev6_user', passwd='cGcd84CDTSY2HH127', 
        #                 db='dev6_base', autocommit=True)
        # self.cHandler = self.myDB.cursor()
        
    def __init__(self, name="dev6"):
        self.dbname = name
        configDict = config.getDbByName(name)
        
        self.myDB = pymysql.connect(host=configDict['host'], port=int(3306), user=configDict['user'],
                                    passwd=configDict['passwd'], db=configDict['database'])

        self.cHandler = self.myDB.cursor()

    def DbConnect168(self):
        return pymysql.connect(host='162.241.85.240', port=int(3306), 
                    user='inforpti_specs', passwd='0p%%jYF7=EYc', 
                    db='inforpti_drivinggears', autocommit=True)
    

    def getTSR(self, VIN):
        sql = '''
                    SELECT *
                    FROM 
                        tbl_service_requests
                    WHERE
                    upc_product_code= '{}';
            '''.format(VIN)
        results     = pd.read_sql_query(sql,self.myDB)
        return results


    def getTBO(self, VIN):
        sql = '''
                    SELECT *
                    FROM 
                        tbl_buyer_offers
                    WHERE
                    upc_product_code= '{}';
            '''.format(VIN)
        results     = pd.read_sql_query(sql,self.myDB)
        return results

    def getTCD(self,VIN):
        sql = '''
                    SELECT *
                    FROM 
                        tbl_closed_deals
                    WHERE
                    upc_product_code= '{}';
            '''.format(VIN)
        results     = pd.read_sql_query(sql, self.myDB)
        return results

    def getBFP(self,VIN):
        sql = '''
                    SELECT *
                    FROM 
                        buyer_finance_parameters
                    WHERE
                    upc_product_code= '{}';
            '''.format(VIN)
        results     = pd.read_sql_query(sql, self.myDB)
        return results

    def getBLP(self,VIN):
        sql = '''
                    SELECT *
                    FROM 
                        buyer_lease_parameters
                    WHERE
                    upc_product_code= '{}';
            '''.format(VIN)
        results     = pd.read_sql_query(sql, self.myDB)
        return results

if __name__ == "__main__":
    dbc = DBConnect(name="dev6")
    print(dbc.getTSR("dfdkjf"))