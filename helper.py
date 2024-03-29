# variables
import csv
TRADE_SIZE = 100
LOG_FILE = 'binance-crypto-trading-bot/trade_log.csv'
TAKER_TRADING_FEE = 0.00075


class OpenOrder:
    def __init__(self, long, target, sl) -> None:
        self.long = long
        self.target = target
        self.sl = sl
        self.completed = False
        self.btcQuant = None

    def trade_executed(self, enter_price, enter_time, fees):
        self.enterPrice = enter_price
        self.enterTime = enter_time
        self.enterfees = fees
        self.btcQuant = TRADE_SIZE/enter_price

        print("ENTRY TRADE")
        data = {
            'LONG': self.long,
            'entry_price': self.enterPrice,
            'entry_time': self.enterTime,
            'target': self.target,
            'SL': self.sl
        }
        print(data)
        # log the entry trade

    def complete_trade(self, exit_price, exit_time, exit_fees):
        self.completed = True
        self.exitPrice = exit_price
        self.exitTime = exit_time
        self.exitFees = exit_fees

        print("EXIT TRADE")
        data = {
            'LONG': self.long,
            'exit_price': self.exitPrice,
            'exit_time': self.exitTime,
            'target': self.target,
            'SL': self.sl
        }
        print(data)
        # log the exit trade

        '''
        log this trade
        calculate profits
        '''

        # LONG TRADE
        if self.long:
            self.profit = self.btcQuant * \
                (self.exitPrice - self.enterPrice)
            outcome = 'PROFIT' if self.enterPrice < self.exitPrice else "LOSS"
            profit_pl = round(self.profit/self.enterPrice, 5) * 100
        # SHORT TRADE
        else:
            self.profit = self.btcQuant * \
                (self.enterPrice - self.exitPrice)
            outcome = 'PROFIT' if self.enterPrice > self.exitPrice else "LOSS"
            profit_pl = round(self.profit/self.exitPrice, 5) * 100
        # STORE to CSV

        data = {
            'POSITION': 'LONG' if self.long else 'SHORT',
            'QUANTITY': round(self.btcQuant, 7),
            'ENTER PRICE': self.enterPrice,
            'EXIT PRICE': self.exitPrice,
            'OUTCOME': outcome,
            'PL VALUE': self.profit,
            'PL PERCENTAGE': profit_pl
        }

        with open(LOG_FILE, 'a') as file:
            writer = csv.DictWriter(file, fieldnames=list(data.keys()))
            writer.writerow(data)


streams1m = 'btcusdt@kline_1m/ethusdt@kline_1m/bnbusdt@kline_1m/xrpusdt@kline_1m/adausdt@kline_1m/dotusdt@kline_1m/dogeusdt@kline_1m/uniusdt@kline_1m/ltcusdt@kline_1m/bchusdt@kline_1m/linkusdt@kline_1m/vetusdt@kline_1m/xlmusdt@kline_1m/solusdt@kline_1m/thetausdt@kline_1m/filusdt@kline_1m/trxusdt@kline_1m/xmrusdt@kline_1m/neousdt@kline_1m/lunausdt@kline_1m/eosusdt@kline_1m/atomusdt@kline_1m/bttusdt@kline_1m/aaveusdt@kline_1m/cakeusdt@kline_1m/fttusdt@kline_1m/etcusdt@kline_1m/mkrusdt@kline_1m/xtzusdt@kline_1m/algousdt@kline_1m/compusdt@kline_1m/runeusdt@kline_1m/avaxusdt@kline_1m/ksmusdt@kline_1m/egldusdt@kline_1m/dashusdt@kline_1m/xemusdt@kline_1m/zecusdt@kline_1m/dcrusdt@kline_1m/chzusdt@kline_1m/snxusdt@kline_1m/hotusdt@kline_1m/hbarusdt@kline_1m/stxusdt@kline_1m/enjusdt@kline_1m/maticusdt@kline_1m/zilusdt@kline_1m/dgbusdt@kline_1m/sushiusdt@kline_1m/batusdt@kline_1m/grtusdt@kline_1m/scusdt@kline_1m/manausdt@kline_1m/yfiusdt@kline_1m/btgusdt@kline_1m/wavesusdt@kline_1m/umausdt@kline_1m/qtumusdt@kline_1m/rvnusdt@kline_1m/ontusdt@kline_1m/zenusdt@kline_1m/bntusdt@kline_1m/hntusdt@kline_1m/zrxusdt@kline_1m/wrxusdt@kline_1m/icxusdt@kline_1m/paxusdt@kline_1m/nanousdt@kline_1m/rsrusdt@kline_1m/oneusdt@kline_1m/ankrusdt@kline_1m/iostusdt@kline_1m/omgusdt@kline_1m/shibusdt@kline_1m'

streams5m = 'btcusdt@kline_5m/ethusdt@kline_5m/bnbusdt@kline_5m/xrpusdt@kline_5m/adausdt@kline_5m/dotusdt@kline_5m/dogeusdt@kline_5m/uniusdt@kline_5m/ltcusdt@kline_5m/bchusdt@kline_5m/linkusdt@kline_5m/vetusdt@kline_5m/xlmusdt@kline_5m/solusdt@kline_5m/thetausdt@kline_5m/filusdt@kline_5m/trxusdt@kline_5m/xmrusdt@kline_5m/neousdt@kline_5m/lunausdt@kline_5m/eosusdt@kline_5m/atomusdt@kline_5m/bttusdt@kline_5m/aaveusdt@kline_5m/cakeusdt@kline_5m/fttusdt@kline_5m/etcusdt@kline_5m/mkrusdt@kline_5m/xtzusdt@kline_5m/algousdt@kline_5m/compusdt@kline_5m/runeusdt@kline_5m/avaxusdt@kline_5m/ksmusdt@kline_5m/egldusdt@kline_5m/dashusdt@kline_5m/xemusdt@kline_5m/zecusdt@kline_5m/dcrusdt@kline_5m/chzusdt@kline_5m/snxusdt@kline_5m/hotusdt@kline_5m/hbarusdt@kline_5m/stxusdt@kline_5m/enjusdt@kline_5m/maticusdt@kline_5m/zilusdt@kline_5m/dgbusdt@kline_5m/sushiusdt@kline_5m/batusdt@kline_5m/grtusdt@kline_5m/scusdt@kline_5m/manausdt@kline_5m/yfiusdt@kline_5m/btgusdt@kline_5m/wavesusdt@kline_5m/umausdt@kline_5m/qtumusdt@kline_5m/rvnusdt@kline_5m/ontusdt@kline_5m/zenusdt@kline_5m/bntusdt@kline_5m/hntusdt@kline_5m/zrxusdt@kline_5m/wrxusdt@kline_5m/icxusdt@kline_5m/paxusdt@kline_5m/nanousdt@kline_5m/rsrusdt@kline_5m/oneusdt@kline_5m/ankrusdt@kline_5m/iostusdt@kline_5m/omgusdt@kline_5m/shibusdt@kline_5m'
stream5m_test = 'btcusdt@kline_5m/ethusdt@kline_5m'
cryptos = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'DOTUSDT', 'DOGEUSDT', 'UNIUSDT', 'LTCUSDT', 'BCHUSDT', 'LINKUSDT', 'VETUSDT', 'XLMUSDT', 'SOLUSDT', 'THETAUSDT', 'FILUSDT', 'TRXUSDT', 'XMRUSDT', 'NEOUSDT', 'LUNAUSDT', 'EOSUSDT', 'ATOMUSDT', 'BTTUSDT', 'AAVEUSDT', 'CAKEUSDT', 'FTTUSDT', 'ETCUSDT', 'MKRUSDT', 'XTZUSDT', 'ALGOUSDT', 'COMPUSDT', 'RUNEUSDT', 'AVAXUSDT', 'KSMUSDT', 'EGLDUSDT', 'DASHUSDT',
           'XEMUSDT', 'ZECUSDT', 'DCRUSDT', 'CHZUSDT', 'SNXUSDT', 'HOTUSDT', 'HBARUSDT', 'STXUSDT', 'ENJUSDT', 'MATICUSDT', 'ZILUSDT', 'DGBUSDT', 'SUSHIUSDT', 'BATUSDT', 'GRTUSDT', 'SCUSDT', 'MANAUSDT', 'YFIUSDT', 'BTGUSDT', 'WAVESUSDT', 'UMAUSDT', 'QTUMUSDT', 'RVNUSDT', 'ONTUSDT', 'ZENUSDT', 'BNTUSDT', 'HNTUSDT', 'ZRXUSDT', 'WRXUSDT', 'ICXUSDT', 'PAXUSDT', 'NANOUSDT', 'RSRUSDT', 'ONEUSDT', 'ANKRUSDT', 'IOSTUSDT', 'OMGUSDT', 'SHIBUSDT']

emptyPositions = {'BTCUSDT': False,
                  'ETHUSDT': False,
                  'BNBUSDT': False,
                  'XRPUSDT': False,
                  'ADAUSDT': False,
                  'DOTUSDT': False,
                  'DOGEUSDT': False,
                  'UNIUSDT': False,
                  'LTCUSDT': False,
                  'BCHUSDT': False,
                  'LINKUSDT': False,
                  'VETUSDT': False,
                  'XLMUSDT': False,
                  'SOLUSDT': False,
                  'THETAUSDT': False,
                  'FILUSDT': False,
                  'TRXUSDT': False,
                  'XMRUSDT': False,
                  'NEOUSDT': False,
                  'LUNAUSDT': False,
                  'EOSUSDT': False,
                  'ATOMUSDT': False,
                  'BTTUSDT': False,
                  'AAVEUSDT': False,
                  'CAKEUSDT': False,
                  'FTTUSDT': False,
                  'ETCUSDT': False,
                  'MKRUSDT': False,
                  'XTZUSDT': False,
                  'ALGOUSDT': False,
                  'COMPUSDT': False,
                  'RUNEUSDT': False,
                  'AVAXUSDT': False,
                  'KSMUSDT': False,
                  'EGLDUSDT': False,
                  'DASHUSDT': False,
                  'XEMUSDT': False,
                  'ZECUSDT': False,
                  'DCRUSDT': False,
                  'CHZUSDT': False,
                  'SNXUSDT': False,
                  'HOTUSDT': False,
                  'HBARUSDT': False,
                  'STXUSDT': False,
                  'ENJUSDT': False,
                  'MATICUSDT': False,
                  'ZILUSDT': False,
                  'DGBUSDT': False,
                  'SUSHIUSDT': False,
                  'BATUSDT': False,
                  'GRTUSDT': False,
                  'SCUSDT': False,
                  'MANAUSDT': False,
                  'YFIUSDT': False,
                  'BTGUSDT': False,
                  'WAVESUSDT': False,
                  'UMAUSDT': False,
                  'QTUMUSDT': False,
                  'RVNUSDT': False,
                  'ONTUSDT': False,
                  'ZENUSDT': False,
                  'BNTUSDT': False,
                  'HNTUSDT': False,
                  'ZRXUSDT': False,
                  'WRXUSDT': False,
                  'ICXUSDT': False,
                  'PAXUSDT': False,
                  'NANOUSDT': False,
                  'RSRUSDT': False,
                  'ONEUSDT': False,
                  'ANKRUSDT': False,
                  'IOSTUSDT': False,
                  'OMGUSDT': False,
                  'SHIBUSDT': False
                  }
