from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import pandas
import logging
import ssl
import json
from json import JSONEncoder

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.dict 

class PyEcoRoot:
    def init(self, currency, eco_element):
        self.currency = currency
        self.eco_element = eco_element

class PyEcoElement:
    def init(self,currency,event, impact,time_eastern, actual,forecast, previous ):
        self.currency = currency
        self.event = event
        self.impact = impact
        self.time_eastern = time_eastern
        self.actual = actual
        self.forecast = forecast
        self.previous = previous

class PyEcoCal:
    def init(self, p1 = 1):
        self.p1 = p1

def GetEconomicCalendar(self,date):
    baseURL = "https://www.forexfactory.com/"

    ssl._create_default_https_context = ssl._create_unverified_context
    
    # ctx = ssl.create_default_context()
    # ctx.check_hostname = False
    # ctx.verify_mode = ssl.CERT_NONE
 
    # html = urllib.request.urlopen(url, context=ctx).read()

    # get the page and make the soup
    urleco = baseURL + date

    opener = urllib.request.build_opener()
    #opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    response = opener.open(urleco)
    result = response.read().decode('utf-8', errors='replace')
    soup = BeautifulSoup(result,"html.parser")
    table = soup.find_all("tr", class_="calendar_row")

    ecoday = []
    for item in table:
        dict = {}
        
        dict["Currency"] = item.find_all("td", {"class":"calendar__currency"})[0].text.strip() #Currency
        dict["Event"] = item.find_all("td",{"class":"calendar__event"})[0].text.strip() #Event Name
        dict["Time_Eastern"] = item.find_all("td", {"class":"calendar__time"})[0].text #Time Eastern
        impact = item.find_all("td", {"class":"impact"})
        
        for icon in range(0,len(impact)):
            dict["Impact"] = impact[icon].find_all("span")[0]['title'].split(' ', 1)[0]

        dict["Actual"] = item.find_all("td", {"class":"calendar__actual"})[0].text #Actual Value
        dict["Forecast"] = item.find_all("td", {"class":"calendar__forecast"})[0].text #forecasted Value
        dict["Previous"] = item.find_all("td", {"class":"calendar__previous"})[0].text # Previous
        
        ecoday.append(dict)

    ecoDict=[]
    
    for item in ecoday:
        rec = ComplexEncoder() 
        ecoelem = PyEcoElement(
             item["Currency"],
             item["Event"],
             item["Impact"],
             item["Time_Eastern"],
             item["Actual"],
             item["Forecast"],
             item["Previous"]
         )
        rec.ecoobject = ecoelem
        ecoDict.append(rec)

    json_object = json.dumps(ComplexEncoder().encode(ecoDict), indent = 3)  
    return json_object