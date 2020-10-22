import pandas as pd
import pymysql


class DBConnect():
    """docstring for DBConnect"""

    def __init__(self):
        self.myDB = pymysql.connect(host='209.126.3.200', port=int(3306), 
                       user='mi_user', passwd='ce251CwE584##878', 
                       db='mi_dbmark', autocommit=True);

        self.cHandler = self.myDB.cursor()

    
    def name_from_VIN (self, upc_product_code):
        '''
        It takes input upc_product_code aka VIN number then verifies from table scrapeData_ column 'upc_product_code' then
        It outputs make,model,trim,year corresponding to it
    '''
        pass

    
    def loadPickle(self, miles, zip_code, make, model,trim, year, upc_product_code=None):
        
        if start_date == '' and end_date == '':
            date_filter_query = ''

        else:
            date_filter_query = '''and  
            STR_TO_DATE(buyer_offers.created_at, '%Y-%m-%d') 
            between STR_TO_DATE('{}', '%Y-%m-%d') and STR_TO_DATE('{}', '%Y-%m-%d')
            '''.format(start_date, end_date)

        sql = '''
        Select 
        (tbl_products.id) as id, 
        (tbl_products.upc_product_code) as  upc_product_code, 
        (tbl_products.seller_email) as seller_email, 
        (tbl_products.catalog_id) as catalog_id,
        (title) as title, 
        (description) as description, 
        (category) as category,
        (sub_category) as sub_category,
        
        (parameter1) as parameter1, 
        (parameter2) as parameter2, 
        (parameter3) as parameter3, 
        (parameter4) as parameter4, 
        (parameter5) as parameter5, 
        (bulk_or_individual) as bulk_or_individual, 
        (product_status) as product_status, 
        (buyer_offers.created_at) as created_at, 
        (buyer_offers.updated_at) as updated_at, 
        (buyer_offer_price) AS buyer_offer_price,  
        (averagePrice) AS avg_buyer_offer_price,
        (buyer_offers.buyer_orignal_quantity) AS buyer_orignal_quantity,
        (buyer_highest_offer_price) AS buyer_highest_offer_price
        from 
        (select *, (buyer_offer_price + buyer_highest_offer_price)/2 as averagePrice
        from tbl_buyer_offers) buyer_offers
        join tbl_products on (tbl_products.upc_product_code = buyer_offers.upc_product_code)
        join tbl_service_requests on (tbl_service_requests.id = buyer_offers.id)
        where 
        tbl_service_requests.api_password = '{}' and
        tbl_products.seller_email = '{}' and
        tbl_products.upc_product_code = '{}'
        
        {}
        '''.format(api_password, seller_email, upc_product_code, date_filter_query)

        results = pd.read_sql_query(sql, self.myDB)
        results['id'] = results['id'].astype(int)
        results['buyer_offer_price'] = results['buyer_offer_price'].astype(float)
        results['avg_buyer_offer_price'] = results['avg_buyer_offer_price'].astype(float)
        results['buyer_highest_offer_price'] = results['buyer_highest_offer_price'].astype(float)

        returnObject = {'success': 'true', 'total_offers': int(len(results.index)),
                        'Lowest_of_buyers_OfferPrice': float(results['buyer_offer_price'].min()),
                        'Highest_of_buyers_OfferPrice': float(results['buyer_offer_price'].max()),
                        'Average_of_buyers_OfferPrice': float(results['avg_buyer_offer_price'].mean()),
                        'Lowest_of_buyers_HighestOfferPrice': float(results['buyer_highest_offer_price'].min()),
                        'Highest_of_buyers_HighestOfferPrice': float(results['buyer_highest_offer_price'].max()),
                        'Average_of_buyers_HighestOfferPrice': float(results['buyer_highest_offer_price'].mean()), 'data': []
        }

        for i in range(0, len(results)):
            lineObject = {'id': int(results.iloc[i]['id']),
                          'upc_product_code': str(results.iloc[i]['upc_product_code']),
                          'title': str(results.iloc[i]['title']), 'description': str(results.iloc[i]['description']),
                          'category': str(results.iloc[i]['category']),
                          'sub_category': str(results.iloc[i]['sub_category']),
                          
                          'parameter1': str(results.iloc[i]['parameter1']),
                          'parameter2': str(results.iloc[i]['parameter2']),
                          'parameter3': str(results.iloc[i]['parameter3']),
                          'parameter4': str(results.iloc[i]['parameter4']),
                          'parameter5': str(results.iloc[i]['parameter5']),
                          'bulk_or_individual': str(results.iloc[i]['bulk_or_individual']),
                          'product_status': str(results.iloc[i]['product_status']),
                          'seller_email': str(results.iloc[i]['seller_email']),
                          'catalog_id': int(results.iloc[i]['catalog_id']),
                          'created_at': str(results.iloc[i]['created_at']),
                          'updated_at': str(results.iloc[i]['updated_at']),
                          'buyer_offer_price': float(results.iloc[i]['buyer_offer_price']),
                          'avgerage_buyer_offer_price': float(results.iloc[i]['avg_buyer_offer_price']),
                          'buyer_orignal_quantity':int(results.iloc[i]['buyer_orignal_quantity']),
                          'buyer_highest_offer_price': float(results.iloc[i]['buyer_highest_offer_price'])
                          }
            returnObject['data'].append(lineObject)
        return returnObject
    
    def query(self, sql_statement):
        sql = sql_statement

        results = pd.read_sql_query(sql, self.myDB)

        return results


if __name__ == '__main__':
    dbObject = DBConnect()
