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
