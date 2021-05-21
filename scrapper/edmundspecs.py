from scrapy.selector import Selector
import requests
import sys
import time
from requests.exceptions import HTTPError
from requests.exceptions import ConnectionError
from random import randrange
from db import DBScrapperConnect
from iautils import dividePagesToThreads
dbc = DBScrapperConnect()
print(dbc.getYearMakeModel())
#https://www.edmunds.com/{}/{}/{}/features-specs/.format(make,model,year)
ckie = 'feature-flags=j%3A%7B%7D; visitor-id=18de7f0a-8667-4d07-bc1d-1f46c9ff1cee; edmunds=18de7f0a-8667-4d07-bc1d-1f46c9ff1cee; session-id=984381633465943000; edw=984381633465943000; usprivacy=1YNN; location=j%3A%7B%22zipCode%22%3A%2258067%22%2C%22latitude%22%3A46.054802%2C%22longitude%22%3A-97.502278%2C%22dma%22%3A%22724%22%2C%22dmaRank%22%3A2%2C%22stateCode%22%3A%22ND%22%2C%22city%22%3A%22Rutland%22%2C%22userSet%22%3Afalse%2C%22ipZipCode%22%3A%2258067%22%2C%22ipDma%22%3A%22724%22%2C%22ipStateCode%22%3A%22ND%22%7D; EdmundsYear="&zip=58067&dma=724:IP&city=Rutland&state=ND&lat=46.054802&lon=-97.502278"; device-characterization=false,false; content-targeting=PK,167,ISLAMABAD,,73.17,33.70,; ak_bmsc=2B402E0F193F2FAB7B41FF87E8C754DBB81C4834B0250000BCFF8B5FD9A9217D~plhGQZyrxNemm18FEAdX6mXF3gPID/irZrCcFl+vbYWqLC4HcUSLIqVqWEjHl+yfn+zQNb7SzgiLyTyBHIk5joc/S6ZMvY0hVcV06RGilzlRYr29y1oMkvyrjnOTcvJDTXoR3MFrlu69zR7LtvRgO9AugwkN7JvKzAo9RL3LgDnv4kMJg7akgNL/0E8OXEsP0eOTrOL8GHJ1EuQqEyFx57629tfsrCIcpPrh+XuxQ7l+w=; lux_uid=160301049757302075; bm_sv=6CFA3DDC11271972485594C3579E5FDB~qTpVm43D2hvtxhTk36w7V4kdhTIxIvXi5NTP9OBLG7xG97qd9PsY9oInfz5PsKRD50/vWVS9gDi/hVUiw0eD5pampbuQReCGv5yNl+oEMFBSJpnly723IbSzpGp8FGYWhvCvZLnWPszclzIquP7TPdvqQRjj490nE3hfhL1wLWs=; _gcl_au=1.1.329637088.1603010498; __gads=ID=aca24e4d28673a7c-228eeaef4ca600b0:T=1603010496:S=ALNI_MYfzxSdWg8odI0WOyWdBctj7OPpsQ; _uetsid=bcddca00111d11ebaa8a37c2cad0d5da; _uetvid=bcde04d0111d11eb80a0af3f91188f99'

headers = {"user-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 GTB7.1 (.NET CLR 3.5.30729)", 
              'content-type': 'text/html',
              "cookie": ckie}
hdr = {"User-Agent": "Googlebot"}
testUrl = 'https://www.edmunds.com/audi/r8/2020/features-specs/'
basdUrl = "https://www.edmunds.com"
#make,model,year
fetchUrl = 'https://www.edmunds.com/{}/{}/{}/features-specs/'



def getConnection(url, params=''):
    
    triesFlag = True
    res = None
    tries = 0
    while(triesFlag):
        try:
            res = requests.get(url=url,headers=hdr)
            triesFlag = False
        except HTTPError as con_err: 
                print('HTTP Error accurred: {}'.format(con_err))
                print('retring... ', tries)
                tries += 1
        except Exception as err: 
                print('HTTP Error accurred: {}'.format(err))
                print('retring... ', tries)
                tries += 1
        time.sleep(randrange(5,10))
    return res

def getValueByText(spage,tag_text):
     return spage.xpath("//th[contains(text(),'{}')]/following-sibling::td/text()".format(tag_text)).get()
def scrapeSpecs(url):
    res = getConnection(url)
    if not res:
        print("page not found: ",url)
        return
    spage = Selector(response=res)
    specs ={}
    specs['most_popular'] = spage.xpath("//div[contains(text(),'Most Popular')]/following-sibling::div/text()").get()
    specs['msrp_price'] = spage.xpath("//th[@data-test='section-header-A']//div[@class='heading-3']/text()").get()
    specs['eng_type'] = getValueByText(spage,'Engine Type')
    specs['drive_type']= getValueByText(spage,'Drive Type')
    specs['trans']= getValueByText(spage,'Transmission')
    specs['eng_cyl']= getValueByText(spage,'Cylinders')
    try: 
        cty_hwy_mpg = getValueByText(spage,'EPA mileage est. (cty/hwy)').replace("mpg","").strip().split("/",1)
    except: 
        cty_hwy_mpg = []
    if len( cty_hwy_mpg) > 1:
        specs['cty_mpg'] = cty_hwy_mpg[0]
        specs['hwy_mpg'] = cty_hwy_mpg[1]
    else:
        specs['cty_mpg'] = ''
        specs['hwy_mpg'] = ''
    specs['fuel_type']= getValueByText(spage,'Fuel type')
    specs['torque']= getValueByText(spage,'Torque')
    specs['horse_power']= getValueByText(spage,'Horsepower')
    specs['length']= getValueByText(spage,'Length')
    specs['width']= getValueByText(spage,'Width')
    specs['weight'] = getValueByText(spage,'Curb weight')
    specs['height']= getValueByText(spage,'Height')
    specs['length']= getValueByText(spage,'Length')
    print(specs)
    make_model_year = url[url.find("com/")+4:url.find('/fea')].split("/",2)
    dbc.saveEdmundsSpecs(make_model_year[0],make_model_year[1],specs['drive_type'],make_model_year[2],
                        specs['horse_power'],specs['trans'],specs['weight'],specs['msrp_price'],specs['eng_type'],
                        specs['eng_cyl'],specs['fuel_type'],specs['width'],
                        specs['height'],specs['length'],specs['torque'],
                        specs['cty_mpg'],specs['hwy_mpg'],specs['most_popular'])
def scraping(carYMM,temp):
    for index in carYMM.index:
        url = fetchUrl.format(carYMM['make'][index],carYMM['model'][index],carYMM['year'][index])
        scrapeSpecs(url)
carYMM = dbc.getYearMakeModel()
scraping(carYMM,1)
#dividePagesToThreads(carYMM,scraping,10,30)
print("finished.......")