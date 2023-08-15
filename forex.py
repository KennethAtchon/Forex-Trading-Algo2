import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

class Oanda:

    def __init__(self,access_token):
        self.access_token = access_token

        self.default_headers = {'Content-Type': 'application/json',
           'Authorization': f'Bearer {self.access_token}'}

        self.default_params = {'instruments': 'EUR_USD,USD_JPY'}

        self.account_endpoint = 'https://api-fxpractice.oanda.com/v3/accounts'

        self.instruments_endpoint = 'https://api-fxpractice.oanda.com/v3/instruments'

        self.account_id = ''

    def getAllAccounts(self):

        response = requests.get(self.account_endpoint, headers=self.default_headers)
        return response.json()
    
    def setCurrentAccount(self, current_id):
        self.account_id = '/' + current_id

        response = requests.get(self.account_endpoint + self.account_id, headers= self.default_headers, params=self.default_params )

        response = response.json()
        if 'errorMessage' in response:
            raise Exception("You have entered the wrong account_id")

    def getAccountSummary(self):
        if self.account_id == '':
            print("Account ID has not been set.")
            return ''
        
        response = requests.get(self.account_endpoint + self.account_id + '/summary', headers=self.default_headers)
        return response.json()

    def getCandles(self, timeframe, count, currency_pair):
        # timeframe format: H5 (4 hours) S5(5 seconds)

        get_candles = self.instruments_endpoint + "/" + currency_pair + "/candles"

        params = {'granularity': timeframe, 'count': count}

        response = requests.get(get_candles, headers=self.default_headers, params=params)

        if 'errorMessage' in response:
            raise Exception("Something went wrong with retrieving candles.")

        return response.json()

    def placeBuyOrder(self, currency_pair, amount, stopLoss, takeProfit):
        
        data = {
        "order": {
            "units": amount,
            "instrument": currency_pair,
            "timeInForce": "FOK",
            "type": "MARKET",
            "positionFill": "DEFAULT"
            }
        }
    
        if takeProfit > 0:
            data["order"]["takeProfitOnFill"] = {"price": takeProfit}
            
        if stopLoss > 0:
            data["order"]["stopLossOnFill"] = {"price": stopLoss}


        response = requests.post(self.account_endpoint + self.account_id + '/orders', headers=self.default_headers, data=json.dumps(data) )

        if response.status_code != 201:
            raise Exception("Could not execute the buy order.")

        return response.json()


    def placeSellOrder(self, currency_pair, amount, stopLoss, takeProfit):
        data = {
        "order": {
            "units": (-amount),
            "instrument": currency_pair,
            "timeInForce": "FOK",
            "type": "MARKET",
            "positionFill": "DEFAULT"
            }
        }
    
        if takeProfit > 0:
            data["order"]["takeProfitOnFill"] = {"price": takeProfit}
            
        if stopLoss > 0:
            data["order"]["stopLossOnFill"] = {"price": stopLoss}


        response = requests.post(self.account_endpoint + self.account_id + '/orders', headers=self.default_headers, data=json.dumps(data) )

        if response.status_code != 201:
            raise Exception("Could not execute the sell order.")

        return response.json()
    
    def placetpOrsl(self, price, type, tradeid):

        print(price)
        data = {
        "order": {
            "timeInForce": "GTC",
            "price": str(price),
            "type": type,
            "tradeID": tradeid
            }
        }

        response = requests.post(self.account_endpoint + self.account_id + '/orders', headers=self.default_headers, data=json.dumps(data) )

        if response.status_code != 201:
            print(response.json())
            raise Exception("Could not execute the tp/sl order.")

        return response.json()


    def getAllOrders(self):
        endpoint = self.account_endpoint + self.account_id + '/orders'
        response = requests.get(endpoint, headers=self.default_headers)

        if response.status_code != 200:
            raise Exception("Could not fetch all orders.")

        return response.json()


    def getAllTrades(self):
        endpoint = self.account_endpoint + self.account_id + '/trades'
        response = requests.get(endpoint, headers=self.default_headers)

        if response.status_code != 200:
            raise Exception("Could not fetch all trades.")

        return response.json()
    
    def getAllTransactions(self):
        endpoint = self.account_endpoint + self.account_id + '/transactions'
        response = requests.get(endpoint, headers=self.default_headers)

        if response.status_code != 200:
            raise Exception("Could not fetch all transactions")

        return response.json()
    
    def getTransactionSince(self, id):
        # params = type: ORDER_FILL
        params = {'id': id,'type': 'ORDER_FILL' }

        endpoint = self.account_endpoint + self.account_id + '/transactions/sinceid'
        response = requests.get(endpoint, headers=self.default_headers, params=params)

        if response.status_code != 200:
            raise Exception("Could not fetch all transactions since " + id)

        return response.json()
    
    def getPositionPair(self, instrument):

        endpoint = self.account_endpoint + self.account_id + "/positions/" + instrument
        response = requests.get(endpoint, headers=self.default_headers)

        if response.status_code != 200:
            raise Exception("Could not fetch position, server returned code: " + str(response.status_code))

        return response.json()
    
    def getAllPositions(self):
        endpoint = self.account_endpoint + self.account_id + "/openPositions"
        response = requests.get(endpoint, headers=self.default_headers)

        if response.status_code != 200:
            raise Exception("Could not fetch positions, server returned code: " + str(response.status_code))

        return response.json()
    
    def getOrderBook(self, instrument):

        endpoint = self.instruments_endpoint + "/" + instrument + "/orderBook"
        response = requests.get(endpoint, headers=self.default_headers)

        if response.status_code != 200:
            raise Exception("Could not fetch order book, server returned code: " + str(response.status_code))

        return response.json()



    
        
oanda = Oanda(os.getenv("ACCESS_TOKEN"))
oanda.setCurrentAccount('101-001-24797201-001')

# EUR_USD pair
# example: oanda.placeSellOrder("EUR_USD", 100, 1.09077, 1.09030)

# timeframe format: H5 (4 hours) S5(5 seconds) M15( 15 minutes)
# Note: this just changes when your getting out, ex: on the 1m could pass ur
# alert but on 1h it doesn't register a new candle in that timeframe
timeframe = "M1"

# what pair are you trading 
instrument = "EUR_USD"

while(True):

    positions = oanda.getAllPositions()

    # checks if there is alr a trade
    if not positions['positions'] or positions['positions'][0]['instrument'] != instrument:
        
        print("Get in there beelzebob")
        # get moving average
        #15m is timeframe of ma
        candleMA = oanda.getCandles("M15", 10 ,instrument)

        sum = 0.0
        
        for i in range(10):
            holder = float(candleMA['candles'][i]['mid']['c'])
            sum += holder
        movingaverage = sum / 10
        movingaverage = round(movingaverage, 5)

        # most recent price
        candle = oanda.getCandles(timeframe, 1 ,instrument)
        recentcandleprice = candle['candles'][0]['mid']['o']

        recentcandleprice = float(recentcandleprice)

        # check if recent price is above or below moving average then buy/sell

        if recentcandleprice >= movingaverage:
            buyorder = oanda.placeBuyOrder(instrument, 100, -1,-1)
            buyprice = float(buyorder['orderFillTransaction']['price'])
            buytradeid = buyorder['orderFillTransaction']['tradeOpened']['tradeID']
            
            # take profit price as relates to buy price , 0.0004 = 4 pips
            takeprofit = buyprice + 0.00041
            # sl
            stoploss = buyprice - 0.00041

            takeprofit = round(takeprofit, 5)
            stoploss = round(stoploss, 5)
            
            oanda.placetpOrsl(takeprofit , "TAKE_PROFIT", buytradeid)
            oanda.placetpOrsl(stoploss, "STOP_LOSS", buytradeid)
        else:
            sellorder = oanda.placeSellOrder(instrument, 100, -1, -1)
            sellprice = float(sellorder['orderFillTransaction']['price'])
            selltradeid = sellorder['orderFillTransaction']['tradeOpened']['tradeID']

            # take profit price as relates to buy price , 0.0004 = 4 pips
            takeprofit = sellprice - 0.0006
            # sl
            stoploss = sellprice + 0.0004

            takeprofit = round(takeprofit, 5)
            stoploss = round(stoploss, 5)
            
            oanda.placetpOrsl(takeprofit , "TAKE_PROFIT", selltradeid)
            oanda.placetpOrsl(stoploss, "STOP_LOSS", selltradeid)



        time.sleep(10)

        

    else:

        print("positions is full waiting to reopen")
        time.sleep(60)







