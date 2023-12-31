import requests
import json
import os
import time
from dotenv import load_dotenv

def calculate_ichimoku_senkou_spans(high_values, low_values):
    # Calculate Tenkan-sen (Conversion Line)
    highest_high = max(high_values[-9:])
    lowest_low = min(low_values[-9:])
    tenkan_sen = (highest_high + lowest_low) / 2

    # Calculate Kijun-sen (Base Line)
    highest_high = max(high_values[-26:])
    lowest_low = min(low_values[-26:])
    kijun_sen = (highest_high + lowest_low) / 2

    # Calculate Senkou Span A (Leading Span A)
    senkou_span_a = (tenkan_sen + kijun_sen) / 2

    # Calculate Senkou Span B (Leading Span B)
    highest_high = max(high_values[-52:])
    lowest_low = min(low_values[-52:])
    senkou_span_b = (highest_high + lowest_low) / 2

    return senkou_span_a, senkou_span_b

def ichimoku_strategy(data_close, senkou_span_a, senkou_span_b):
    current_close = data_close[-1]
    current_senkou_span_a = senkou_span_a
    current_senkou_span_b = senkou_span_b

    # Condition for buy signal
    if (current_close > current_senkou_span_a and
        current_close > current_senkou_span_b):
        return "Buy"

    # Condition for sell signal
    elif (current_close < current_senkou_span_a or
          current_close < current_senkou_span_b):
        return "Sell"

    # No trade signal
    else:
        return "Hold"






# signals = adx_strategy(high_values, low_values, close_values)
# print(signals)


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
            print(response.json())
            raise Exception("Could not fetch position, server returned code: " + str(response.status_code))

        return response.json()
    
    def getAllPositions(self):
        endpoint = self.account_endpoint + self.account_id + "/openPositions"
        response = requests.get(endpoint, headers=self.default_headers)

        if response.status_code != 200:
            print(response.json())
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

# what pair are you trading 
instruments = ["USD_JPY", "EUR_USD", "EUR_JPY", "AUD_JPY", "USD_CAD", "GBP_USD", "EUR_CHF", "USD_CHF", "AUD_USD", "CAD_CHF",
    "NZD_USD", "USD_SGD", "USD_HKD", "USD_SEK",
    "USD_NOK", "USD_DKK", "USD_TRY", "USD_MXN",
    "USD_ZAR", "USD_CNH", "USD_HUF", "USD_PLN",
    "USD_INR", "USD_THB", "USD_IDR", "USD_MYR"]

instrumentIndex = 0


# take profit pips [0] = JPY , [1] = other pairs
takeprofitpips = [0.20, 0.0010]

# stop loss pips [0] = JPY, [1] = other pairs
stoplosspips = [0.10, 0.0005]

# round number,[0] 2 = JPY, [1] 5 = other pairs
roundnum = [2,5]

pairpips = {'JPY': 0, 'USD': 1}

period = 52

while(True):
    instrument = instruments[instrumentIndex % 5]
    print(instrument + " index: " + str(instrumentIndex))

    currentpair = ""
    if 'JPY' in instrument:
        currentpair = "JPY"
    else:
        currentpair = "USD"

    positions = oanda.getPositionPair(instrument)

    # checks if there is alr a trade
    if positions['position']['long']['units'] == '0' and positions['position']['short']['units'] == '0':
        
        print("Opening a position")
        #15m is timeframe of ma
        candles = oanda.getCandles("M15", period ,instrument)

        high_values = [float(candle['mid']['h']) for candle in candles['candles']]  # List of high values for each candle
        low_values = [float(candle['mid']['l']) for candle in candles['candles']]   # List of low values for each candle
        close_values = [float(candle['mid']['c']) for candle in candles['candles']] # List of close values for each candle

        span_a, span_b = calculate_ichimoku_senkou_spans(high_values, low_values)
        print("Senkou Span A:", span_a)
        print("Senkou Span B:", span_b)

        signal = ichimoku_strategy(close_values, span_a, span_b)
        print("Signal:", signal)
                


        if signal == "Buy":
            buyorder = oanda.placeBuyOrder(instrument, 100000, -1,-1)
            buyprice = float(buyorder['orderFillTransaction']['price'])
            buytradeid = buyorder['orderFillTransaction']['tradeOpened']['tradeID']
            

            takeprofit = buyprice + takeprofitpips[pairpips[currentpair]]
            stoploss = buyprice - stoplosspips[pairpips[currentpair]]

            takeprofit = round(takeprofit, roundnum[pairpips[currentpair]])
            stoploss = round(stoploss, roundnum[pairpips[currentpair]])


            oanda.placetpOrsl(takeprofit , "TAKE_PROFIT", buytradeid)
            oanda.placetpOrsl(stoploss, "STOP_LOSS", buytradeid)

        elif signal == "Sell":
            sellorder = oanda.placeSellOrder(instrument, 100000, -1, -1)
            sellprice = float(sellorder['orderFillTransaction']['price'])
            selltradeid = sellorder['orderFillTransaction']['tradeOpened']['tradeID']

            
            takeprofit = sellprice - takeprofitpips[pairpips[currentpair]]
            stoploss = sellprice + stoplosspips[pairpips[currentpair]]

            takeprofit = round(takeprofit, roundnum[pairpips[currentpair]])
            stoploss = round(stoploss, roundnum[pairpips[currentpair]])
            
            oanda.placetpOrsl(takeprofit , "TAKE_PROFIT", selltradeid)
            oanda.placetpOrsl(stoploss, "STOP_LOSS", selltradeid)


        instrumentIndex += 1
        time.sleep(10)

    else:

        print("positions is full waiting to reopen")
        instrumentIndex += 1
        time.sleep(60)


