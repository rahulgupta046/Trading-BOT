# trading-bot

> A cryptocurrency trading bot that automates long and short trades on a bunch of USDT pairs. It uses a user customizable strategy choosing from a set of technical indicators
## Warning

**This bot is not intended to make anyone rich or make money. Its main purpose is educational and learn about the exchange API, websockets, some candlestick or signal processing**

**Use it at your own risk. I am not responsible for any loss incurred directly or indirectly by using this code.**

## Main features

- The bot works with a bunch of USDT pairs that can be modified at _variables.py_ file.
- Use of Binance API in order to obtain past candlestick price information.
- Use of WebSockets and streaming sockets in order to retrieve real-time candlestick data from Binance.
- The default timeframe is 1 hr candlestick, the user can change it to their preference.
- Candlestick processing and indicator calculations in real-time.
- Wallet simulation so the user can test the bot without investing real money or creating a Binance account.

## Trading bot

### Strategy
Users can select from multiple technical indicators with customizable parameters individually or in a group to decide when the trade is made. By default only 1 trade at a time with only 1 asset. 

### How does it work?

With the default 1 hr timeframe, first it waits the optimum time once to retrieve old data and start listening to the real-time WebSocket once the trading bot starts running. That is done because getting API data is not instant and can take more than a minute to get all the past candlesticks for all the pairs. It simply makes sure that there is sufficient time to do things before a 1-hr candle closes. (wait a minute after the candle close and place a market order when the indicator gives the signal.)

Then starts running the WebSocket. Because we have previously waited, we can now retrieve past candlestick data. This process also cleans and processes the data to use less memory and faster later access.

Each time the WebSocket receives data, it first checks that the candlestick is indeed closed, then starts calculating indicator values and conditions in order to make buy or sell actions.

The bot makes long and short trades according to the strategy. Once it makes a buy or sell action, it logs to the console and to the _.json_ file, in order to send the data to the user using the Telegram bot.

### Some constants that can be changed

- `RSI_PERIOD = 14`: The period of RSI calculation (RSI not used by default, but the user can use it to check for market conditions)
- `INIT_USDT = 1000`: Initial USDT amount to invest
- `INIT_BNB = 10`: Initial BNB amount to pay fees

- `MAX_CURRENT_CRYPTOS = 20`: Stop buying if this number of positions are open. Also, it will be invested the current USDT divided by `MAX_CURRENT_CRYPTOS` on each trade.
- `MIN_USDT = 200`: Stop buying if this amount of current USDT is reached

- `RRRATIO = 1.5`: Risk Reward Ratio for the target price calculation
- `LEVERAGE = 5`: Leverage for margin trading
- `MAKERFEERATE = 0.00018`: The percentage (per one) of maker fee
- `TAKERFEERATE = 0.00036`: The percentage (per one) of taker fee

## Telegram bot

### How does it work?

Each time the trading bot makes a trade, it will log the information in a _.json_ file. So, the Telegram bot can have access to that information, without blocking the main thread of the trading bot.

So, the Telegram bot actually runs in paral·lel and does not interfere with the trading bot. You can choose wether to run the telegram bot or not. The telegram bot can not in any circumstances send orders to the trading bot, so the user does not directly interact with it. It only informs the user as they ask for information.

The Telegram bot only sends information to a single specific user, so you have to type the user ID on top of _telegram_bot.py_ so the bot can check that it is indeed sending information only to the desired user. The user ID is a number that can be seen each time a user sends a message to the Telegram bot.

It is useful to track trade information on the go, so you do not have to look at the console every time, which may be tedious. Each time a trade is made, it will send a message with the trade information. Each trade has a unique ID that is shared between the buy and sell action. For example, the bot detects a signal and buys some tokens from a pair. That buy signal would have an ID. When the bot sells that pair, it will have the same ID, so you can track the trade easily.

## Set up

### Install Python dependencies

Run the following line in the terminal: `pip install -r requirements.txt`.

You may create a `virtualenv` to execute this project, to know more about how to install and create virtualenvs visit [virtualenv](https://docs.python.org/3/library/venv.html).

## Authors

This project is created and maintained by Rahul Gupta.

## Disclaimer

This project is for informational and educational purposes only. The user must not use the project or anything related to it as investment, financial or other advice.

There is not any warranty that the information and materials contained in this project are accurate.

**USE AT YOUR OWN RISK!**

Under any circumstances will the author of the project be held responsible or liable in any way for claims, damages, losses, expenses, costs, or liabilities watsoever, including, without limitation, any direct or indirect damages for loss of profits.
