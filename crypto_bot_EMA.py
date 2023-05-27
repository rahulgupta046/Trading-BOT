import websocket
import json
import requests
import time
import json
from indicators import MACD, RSI, VolumeIndicator
from helper import TRADE_SIZE, OpenOrder, TAKER_TRADING_FEE
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from binance.client import Client
from datetime import datetime, timedelta
import os
import threading
load_dotenv()


def init_wallet():
    global wallet
    wallet['USDT'] = INIT_USDT
    wallet['BNB'] = INIT_BNB
    wallet['BTCUSDT'] = 0

    print("wallet initialized")


def getBnbPrice():
    # Get BNB price to calculate exact fees
    url = 'https://api.binance.com/api/v3/avgPrice?symbol=BNBUSDT'
    return float(requests.get(url).json()['price'])


def calculate_function(long):
    global stream
    latest_price = stream.iloc[-1]['Price']

    if long:
        stop_loss = latest_price * (1 - RISK_PERCENTAGE / 100)
        target = latest_price / (1 + RRRATIO * RISK_PERCENTAGE / 100)
    else:
        stop_loss = latest_price(1 + RISK_PERCENTAGE / 100)
        target = latest_price / (1 - RRRATIO * RISK_PERCENTAGE / 100)
    return target, stop_loss


'''
Function to get past data and init indicators based on hat past data
returns indicator objects and the previous data -> data, macd, rsi, volume indicator
'''


def get_data():
    # Define the column names for the DataFrame
    columns = ['open_time', 'open', 'high', 'low', 'close', 'volume']

    # Create an empty DataFrame
    df = pd.DataFrame(columns=columns)
    # Get Past one hour data and store into database

    # Calculate the start and end timestamps for the desired 1-hour period
    end_time = str(datetime.utcnow())
    start_time = str(datetime.utcnow() - timedelta(hours=1))
    interval = Client.KLINE_INTERVAL_1MINUTE

    # Retrieve the Kline data from the Binance API
    klines = client.get_historical_klines(
        symbol=symbol,
        interval=interval,
        start_str=str(start_time),
        end_str=str(end_time)
    )

    # Iterate over the retrieved Kline data and insert it into the database
    for kline in klines:
        # Convert milliseconds to seconds
        open_time = pd.to_datetime(int(kline[0]), unit='ms')
        open_price = float(kline[1])
        high_price = float(kline[2])
        low_price = float(kline[3])
        close_price = float(kline[4])
        volume = float(kline[5])

        # Append a new row to the DataFrame
        row = pd.DataFrame([[open_time, open_price, high_price,
                             low_price, close_price, volume]], columns=columns)
        df = pd.concat([df, row], ignore_index=True)

    # Init Indicators
    macd = MACD(data=df)
    rsi = RSI(data=df)
    volumeIndicator = VolumeIndicator(data=df)

    return [df, macd, rsi, volumeIndicator]


'''
Function to get the BNB fees for transaction
returns float value representing fees in BNB
'''


def get_fees():
    bnb_price = getBnbPrice()
    # Buying for TRADE_SIZE usdt
    bnb_fees = TRADE_SIZE * TAKER_TRADING_FEE/bnb_price
    return bnb_fees


'''
function to check prerequisite
returns bool value
'''


def prereq():
    global wallet
    print("checking prereq")
    print(wallet)
    if wallet['BNB'] < get_fees():
        print("ADD MORE BNB")
    return wallet['USDT'] > TRADE_SIZE and wallet['BNB'] > get_fees()


'''
function to execute orders with binance or locally
First created locally
'''


def execute_order(order, triggered):
    print("exec order checking")
    global stream, open_orders, open_position

    latest_row = stream.iloc[-1]
    trade_time, trade_price, trade_fees = latest_row['Time'], latest_row['Price'], get_fees(
    )

    if triggered == False:
        # just place order with order type and keep it market order.
        order.trade_executed(trade_price, trade_time, trade_fees)
        # Check order type
        if order.long:
            # BUY ORDER
            # changes to the wallet
            wallet['USDT'] -= 10
            wallet['BNB'] -= trade_fees
            wallet['BTC'] += order.btcQuant
        else:
            # SELL ORDER
            wallet['USDT'] += 10
            wallet['BNB'] -= trade_fees
            wallet['BTC'] -= order.btcQuant

    else:
        # market order
        order.complete_trade(trade_price, trade_time, trade_fees)
        open_position = False
        # Check order type
        if order.long:
            # closing BUY ORDER => sell btc
            # changes to the wallet
            wallet['USDT'] += trade_price * order.btcQuant
            wallet['BNB'] -= trade_fees
            wallet['BTC'] -= order.btcQuant
        else:
            # closing SELL ORDER => buy back btc
            wallet['USDT'] -= trade_price * order.btcQuant
            wallet['BNB'] -= trade_fees
            wallet['BTC'] += order.btcQuant
    print("exec order checked")


'''
    Function to handle message from socket on price ticker
    also checks if open trade is triggered or not
'''


def handle_price_message(ws, msg):
    global stream, open_position, open_orders
    symbol, time, price = msg['s'], msg["E"], msg['c']

    df = {
        'Symbol': symbol,
        'Time': pd.to_datetime(time, unit='ms'),
        'Price': float(price)
    }
    row = pd.DataFrame(df, index=[0])
    stream = pd.concat([stream, row], ignore_index=True)

    # check close position on latest candle
    if open_position:
        temp = open_orders[0]
        if temp.long and (price < temp.sl or price > temp.target):
            execute_order(temp, True)
        if not temp.long and (price > temp.sl or price < temp.target):
            execute_order(temp, True)


'''
    Function to handle message from on candlestick
'''


def handle_kline_message(ws, msg):
    # print("Type is - ")
    # when candle is closed
    if msg['k']['x'] == False:
        pass
    elif msg['k']['x'] == True:
        print("Candle Received")

        # reset datastream
        global stream, data, open_position, macdIndicator, rsiIndicator, volumeIndicator, open_orders
        stream = pd.DataFrame(columns=['Symbol', 'Time', 'Price'])

        columns = ['open_time', 'open', 'high', 'low', 'close', 'volume']
        # Extract the relevant data from the WebSocket message
        open_time = pd.to_datetime(int(msg['k']['t']), unit='ms')
        open_price = float(msg['k']['o'])
        high_price = float(msg['k']['h'])
        low_price = float(msg['k']['l'])
        close_price = float(msg['k']['c'])
        volume = float(msg['k']['v'])
        # Append a new row to the DataFrame
        row = pd.DataFrame([[open_time, open_price, high_price,
                             low_price, close_price, volume]], columns=columns)
        data = pd.concat([data, row],  ignore_index=True)

        # update indicators and get signals
        signals = {}
        signals['MACD'] = macdIndicator.update_trade_signal(data)
        signals['RSI'] = rsiIndicator.update_trade_signal(data)
        signals['volume'] = volumeIndicator.get_signal(data)

        if open_position == False and prereq():
            # CONDITION FOR LONG TRADE
            if signals['MACD'] == signals["RSI"] == "Buy" and signals['volume']:
                open_position = True
                long = True
                print("-------------------LONG TRADE----------------------------")
                # calculate target and stop loss
                target, sl = calculate_function(long)
                # trade_time = pd.to_datetime(msg['E'], unit='ms')
                order = OpenOrder(long, target, sl)
                open_orders = [order]
                # execute trade and get the buy price
                execute_order(order, False)

            # CONDITION FOR SHORT TRADE
            elif signals['MACD'] == signals["RSI"] == "Sell" and signals['volume']:
                open_position = True
                long = False
                print("-------------------SHORT TRADE----------------------------")
                # calculate target and stop loss
                target, sl = calculate_function(long)

                # trade_time = pd.to_datetime(msg['E'], unit='ms')
                order = OpenOrder(long, target, sl)
                open_orders = [order]
                # execute trade and get the buy price
                execute_order(order, False)

            else:
                print("-------------------NO TRADE----------------------------")
        # Position is already open, cannot take another position for now
        else:
            print("Already one position is open")


'''
    Function to initialize socket
'''


def init_socket():
    base_url = 'wss://stream.binance.com:9443/stream?streams=btcusdt@ticker/btcusdt@kline_1m'
    streams = {
        'price': 'btcusdt@ticker',
        'candle': 'btcusdt@kline_1m'
    }

    def on_open(ws):
        print("open")

    def on_message(ws, msg):
        data = json.loads(msg)
        stream_name = data['stream']

        if stream_name == streams['price']:
            handle_price_message(ws, data['data'])

        if stream_name == streams['candle']:
            handle_kline_message(ws, data['data'])

    def on_error(ws, err):
        print("Error with the socket - ", err)
        # TODO - consider already open offers.

    def on_close(ws):
        # WebSocket connection closed
        print("WebSocket connection closed")
    stream_socket = websocket.WebSocketApp(base_url,
                                           on_open=on_open,
                                           on_message=on_message,
                                           on_error=on_error,
                                           on_close=on_close
                                           )

    stream_socket.run_forever()


# Constants
INIT_USDT = 1000
INIT_BNB = 10  # Needed to pay fees

RRRATIO = 2  # Risk Reward Ratio
RISK_PERCENTAGE = 2

apiKey = os.getenv('API_KEY')
secretKey = os.getenv('SECRET_KEY')

"""
A little explanation on how leverage positions are coded.
Opening a position is buying from now on, even it is a short position, it is
still considered buying.
Closing a position is selling from now on, even it is a short position, it is
still considered selling.

When buying:
    - The total USDT spent recorded on the code is the initial margin price.
    - The number of coins owned are the equivalent of margin*LEVERAGE.
    - Example: Buy 50€ of VET at 0.08 with LEVERAGE=5
        - usdt spent: 50 USDT
        - actual position price (not logged on tradeHistory): 50*5 = 250 USDT
        - coins owned: 250 USDT/0.08(USDT/VET) = 3125 VET

When selling:
    - The total USDT earned is the initial margin + profit.

"""


""" Indicates how many coins are in the wallet
    wallet[crypto] = (amount, priceOfBuy, long)
        long = True if long position
               False if short position 
"""
wallet = {}

init_wallet()

symbol = 'BTCUSDT'
client = Client(api_key=apiKey, api_secret=secretKey)
open_position = False
# to store the open order object
open_orders = []
data, macdIndicator, rsiIndicator, volumeIndicator = get_data()

stream = pd.DataFrame(columns=['Symbol', 'Time', 'Price'])

# print('data')
# print(data.tail)

# print('indicators')
# print('MACD')
# print(macd.macd_data)

# print('RSI')
# print(rsi.rsi_values)

# print("volume")
# print(volume.volume)
# threading.Thread(target=receive_stream).start()
threading.Thread(target=init_socket).start()

while True:
    time.sleep(20)
    print(stream.shape, data.shape)
