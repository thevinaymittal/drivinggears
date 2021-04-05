import os
config_path = os.path.dirname(os.path.abspath(__file__))
#print(config_path)
#Local Instance
configLocalDict={}
configLocalDict['customerPath'] = '/var/www/ai.robonegotiator.online/testcutomerdata.csv'
configLocalDict['dealPath'] =  '/var/www/ai.robonegotiator.online/mapped_deal_customers.csv'
configLocalDict['csvToSql'] = 1
configLocalDict['host'] = 'localhost'
configLocalDict['port'] = 3306
configLocalDict['user'] = 'root'
configLocalDict['passwd'] = '123'
configLocalDict['database'] = 'beta_base'
configLocalDict['getMostCommonDemographics'] = 'http://mi.robonegotiator.com/api/api/getMostCommonDemographics'
configLocalDict['wkhtmltopdfDirectory'] =''
#Production instance 
configProdDict={}
configProdDict['customerPath'] = '/var/www/mi.robonegotiator.online/testcutomerdata.csv'
configProdDict['dealPath'] =  '/var/www/mi.robonegotiator.online/mapped_deal_customers.csv'
configProdDict['csvToSql'] = 1
configProdDict['host'] = '209.126.3.200'
configProdDict['port'] = 3306
configProdDict['user'] = 'beta_user'
configProdDict['passwd'] = 'cEe8dcSSd84dHH012'
configProdDict['database'] = 'beta_base'
configProdDict['getMostCommonDemographics'] = 'http://mi.robonegotiator.com/api/api/getMostCommonDemographics'
configProdDict['wkhtmltopdfDirectory'] ='a'
configDict = configProdDict # select manually between configLocalDict or configProdDict
#Scrapper Db
configScrapperDict={}
configScrapperDict['host'] = '209.126.3.200'
configScrapperDict['port'] = 3306
configScrapperDict['user'] = 'mi_user'
configScrapperDict['passwd'] = 'ce251CwE584##878'
configScrapperDict['database'] = 'mi_dbmark'

db = {'name':['dev6','api','beta'],'user':['dev6_user','api_user','beta_user'],'passwd':['cGcd84CDTSY2HH127','RM1Z7HmKe2MVHH256','cEe8dcSSd84dHH012'],'database':['dev6_base','api_base','beta_base']}
Dbs = [configLocalDict, configProdDict, configScrapperDict]
def getIndexByName(name):
        print(db['name'])
        for index, n in enumerate(db['name']):
            if n == name:
                return index
        return 0

def getDbByName(name):
    index = getIndexByName(name)
    name = db['name'][index]
    db_user = db['user'][index]
    db_pass = db['passwd'][index]
    db_dbname = db['database'][index]

    for dbConfig in Dbs:
        dbConfig['user'] = db_user
        dbConfig['passwd'] = db_pass
        dbConfig['database'] = db_dbname
    return Dbs[1]

    








