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
# Constants
INIT_USDT = 1000
INIT_BNB = 10  # Needed to pay fees

RRRATIO = 2  # Risk Reward Ratio
RISK_PERCENTAGE = 1
wallet = {}
wallet['USDT'] = INIT_USDT
wallet['BNB'] = INIT_BNB
wallet['BTC'] = 0


def getBnbPrice():
    # Get BNB price to calculate exact fees
    url = 'https://api.binance.com/api/v3/avgPrice?symbol=BNBUSDT'
    return float(requests.get(url).json()['price'])


def getBTCPrice():
    url = 'https://api.binance.com/api/v3/avgPrice?symbol=BTCUSDT'
    return float(requests.get(url).json()['price'])


def get_fees():
    bnb_price = getBnbPrice()
    # Buying for TRADE_SIZE usdt
    bnb_fees = TRADE_SIZE * TAKER_TRADING_FEE/bnb_price
    return bnb_fees


def calculate_function(long, latest_price):
    if long:
        stop_loss = latest_price * (1 - RISK_PERCENTAGE / 100)
        target = latest_price * (1 + RRRATIO * RISK_PERCENTAGE / 100)
    else:
        stop_loss = latest_price*(1 + RISK_PERCENTAGE / 100)
        target = latest_price * (1 - RRRATIO * RISK_PERCENTAGE / 100)
    return target, stop_loss


apiKey, secretKey = os.getenv('API_KEY'), os.getenv('SECRET_KEY')
symbol = 'BTCUSDT'
client = Client(api_key=apiKey, api_secret=secretKey)

columns = ['open_time', 'open', 'high', 'low', 'close', 'volume']

# Create an empty DataFrame
df = pd.DataFrame(columns=columns)
# Get Past one hour data and store into database

# Calculate the start and end timestamps for the desired 1-hour period
end_time = str(datetime.utcnow())
# past 6 months data
start_time = str(datetime.utcnow() - timedelta(hours=1000))

# Retrieve the 5min Kline data from the Binance API
klines = client.get_historical_klines(
    symbol=symbol,
    interval=Client.KLINE_INTERVAL_5MINUTE,
    start_str=str(start_time),
    end_str=str(end_time)
)

print("WE HAVE THE CANDLES")
rsi = RSI(df)
open_position = False
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

    signal = rsi.update_trade_signal(df)

    if open_position == False:
        # CONDITION FOR LONG TRADE
        if signal == "Buy":
            open_position = True
            long = True
            print("-------------------LONG TRADE----------------------------")
            # calculate target and stop loss
            target, sl = calculate_function(long, close_price)
            order = OpenOrder(long, target, sl)
            open_orders = [order]
            order.trade_executed(close_price, open_time, get_fees())
            wallet['USDT'] -= TRADE_SIZE
            wallet['BNB'] -= order.enterfees
            wallet['BTC'] += order.btcQuant

        # CONDITION FOR SHORT TRADE
        elif signal == "Sell":
            open_position = True
            long = False
            print("-------------------SHORT TRADE----------------------------")
            # calculate target and stop loss
            target, sl = calculate_function(long, close_price)

            # trade_time = pd.to_datetime(msg['E'], unit='ms')
            order = OpenOrder(long, target, sl)
            open_orders = [order]
            order.trade_executed(close_price, open_time, get_fees())
            wallet['USDT'] -= TRADE_SIZE
            wallet['BNB'] -= order.enterfees
            wallet['BTC'] += order.btcQuant
    if open_position == True:
        # check for close
        od = open_orders[0]
        if od.long:
            if high_price >= od.target:
                order.complete_trade(od.target, open_time, get_fees())
                # profit in trade, close long trade
                wallet['USDT'] += od.target * order.btcQuant
                wallet['BNB'] -= get_fees()
                wallet['BTC'] -= order.btcQuant
                print(wallet)
                open_position = False
            elif low_price <= od.sl:
                order.complete_trade(od.sl, open_time, get_fees())
                # loss in trade, close long trade
                wallet['USDT'] += od.sl * order.btcQuant
                wallet['BNB'] -= get_fees()
                wallet['BTC'] -= order.btcQuant
                open_position = False
                print(wallet)
        else:
            if low_price <= od.target:
                order.complete_trade(od.target, open_time, get_fees())
                # profit in trade, close long trade
                wallet['USDT'] += od.target * order.btcQuant
                wallet['BNB'] -= get_fees()
                wallet['BTC'] -= order.btcQuant
                open_position = False
            elif high_price >= od.sl:
                order.complete_trade(od.sl, open_time, get_fees())
                # profit in trade, close long trade
                wallet['USDT'] += od.sl * order.btcQuant
                wallet['BNB'] -= get_fees()
                wallet['BTC'] -= order.btcQuant
                open_position = False
    # print(open_price, close_price, high_price, low_price)
