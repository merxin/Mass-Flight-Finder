import requests
from datetime import datetime, timedelta
import pandas as pd

data = pd.read_excel('FlightFinder.xlsx')
TEQUILA_ENDPOINT = "https://api.tequila.kiwi.com/v2/search"
TEQUILA_ENDPOINT2 = "https://api.tequila.kiwi.com/locations/query"
TEQUILA_API_KEY = YOUR API KEY

format = "%Y-%m-%dT%H:%M:%S.000Z"
headers = {'apikey': TEQUILA_API_KEY}

class Iata:
#searches for airport id using location API
    def __init__(self, city):
        self.city = city

    def GetIataCode(self):
        self.location_endpoint = TEQUILA_ENDPOINT2
        self.headers = {"apikey": TEQUILA_API_KEY}
        self.query = {"term": self.city, "location_types": "city"}
        self.response = requests.get(url=self.location_endpoint, headers=self.headers, params=self.query)
        self.results = self.response.json()["locations"]
        #print(self.results)
        self.iAta = self.results[0]["code"]
        return self.iAta


class Flights:
""" uses search API to find the details of the cheapest flight for a particular pair of cities """
    def __init__(self, headers, query):
        self.headers = headers
        self.query = query
        #print("self query",self.query)
        self.response = requests.get(TEQUILA_ENDPOINT, headers=self.headers, params=self.query)
        self.price=int(self.response.json()['data'][0]['price'])
        self.connecting_flights = []
        #print("FlightSearch JSON",self.response.json())
        try:
            for i in range (0, self.query['max_stopovers']*2):
                self.route = self.response.json()['data'][0]['route'][i]['cityFrom'] + '-' + self.response.json()['data'][0]['route'][i]['cityTo']
                self.time_of_departure=self.response.json()['data'][0]['route'][i]['local_departure']
                self.time=(datetime.strptime(self.time_of_departure, format))
                self.connecting_flights.append(str(self.time) +" "+ self.route)
                #print(self.connecting_flights)

        except IndexError:
            pass

    def List_of_connecting_flights(self):
        return self.connecting_flights



    def GetPrice(self):
        return self.price

    def GetDeparture(self):
        return self.connecting_flights[0][:16]

    def GetReturnHome(self):
        return self.connecting_flights[-1][:16]



dest_list = data['Destination'].to_list()
origin_list = data['Origin'].to_list()

flight_list = data.to_dict('records')
for i in range(0,len(flight_list)):
    flight_list[i]['date_from'] = flight_list[i]['date_from'].strftime("%d/%m/%Y")
    flight_list[i]['date_to'] = flight_list[i]['date_to'].strftime("%d/%m/%Y")
    flight_list[i]['fly_from'] = Iata(origin_list[i]).GetIataCode()
    flight_list[i]['fly_to'] = Iata(dest_list[i]).GetIataCode()
    del flight_list[i]['Origin']
    del flight_list[i]['Destination']
    for key in ("nights_in_dst_from", "nights_in_dst_to", "max_stopovers", "one_for_city"):
        flight_list[i][key]= int(flight_list[i][key])
    #print(origin_list[i])
    #print(flight_list[i])



#print("Flight List list of dicts",flight_list)
#print(flight_list[0])


for i in range(0, len(flight_list)):
    try:
         c=Flights(headers, flight_list[i])
         data.loc[i, 'Price'] = c.GetPrice()
         data.loc[i, 'Departure'] = c.GetDeparture()
         data.loc[i, 'Return'] = c.GetReturnHome()
         n=1
         for j in c.List_of_connecting_flights():
             Connection =f"Connection {n}"
             data.loc[i,Connection]=j
             n+=1
    except IndexError:
        data.loc[i, 'Price'] = (f"not enough stopovers for {data.loc[i, 'Origin']} - {data.loc[i, 'Destination']}")
data.drop('fly_from', inplace=True, axis=1)
data.drop('fly_to', inplace=True, axis=1)
data.drop('date_from', inplace=True, axis=1)
data.drop('date_to', inplace=True, axis=1)
data.drop('nights_in_dst_from', inplace=True, axis=1)
data.drop('nights_in_dst_to', inplace=True, axis=1)
data.drop('one_for_city', inplace=True, axis=1)
data.drop('max_stopovers', inplace=True, axis=1)
data.to_excel('FlightFinder3.xlsx')


