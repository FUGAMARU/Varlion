import pytz
import os

ROOT_DIR = os.getcwd()

UTC = pytz.timezone("Etc/UTC")
JST = pytz.timezone("Asia/Tokyo")

SYMBOLS = ["USDJPY", "EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDCAD", "USDCHF", "EURJPY", "GBPJPY", "AUDJPY", "NZDJPY", "CADJPY", "CHFJPY", "CADCHF", "EURCAD", "EURCHF", "EURGBP", "GBPCAD", "GBPCHF", "AUDCAD", "AUDCHF", "AUDNZD", "EURAUD", "EURNZD", "GBPAUD", "GBPNZD", "NZDCAD", "NZDCHF"]
CURRENCIES = ["EUR", "USD", "JPY", "CHF", "GBP", "AUD", "CAD", "NZD"]
