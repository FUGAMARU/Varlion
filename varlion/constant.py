import pytz
import os

ROOT_DIR = os.getcwd()

UTC = pytz.timezone("Etc/UTC")
JST = pytz.timezone("Asia/Tokyo")

SYMBOLS = ["USDJPY", "EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDCAD", "USDCHF", "EURJPY", "GBPJPY", "AUDJPY", "NZDJPY", "CADJPY", "CHFJPY", "CADCHF", "EURCAD", "EURCHF", "EURGBP", "GBPCAD", "GBPCHF", "AUDCAD", "AUDCHF", "AUDNZD", "EURAUD", "EURNZD", "GBPAUD", "GBPNZD", "NZDCAD", "NZDCHF"]
CURRENCIES = ["EUR", "USD", "JPY", "CHF", "GBP", "AUD", "CAD", "NZD"]

ACCOUNT_NUMBER = 0
PASSWORD = ""
SERVER = ""

FILLING_TYPE = ""
LOT = 0
STOPLOSS = 0

SINCE = 0
UNTIL = 0
SHORT_SMA = 0
LONG_SMA = 0

SERVER_TIMEZONE = ""
USE_EXTERNAL_SOURCE = None
SOURCE_URL = ""
LINE_PREFIX = ""
