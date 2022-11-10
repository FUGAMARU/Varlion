import datetime
import math
import MetaTrader5 as mt5

from config import SERVER_TIMEZONE
from constant import SYMBOLS, CURRENCIES, UTC


def get_original_currency_strength() -> dict[str, float] | None:
    """ 独自に計算した当日分の現在における通貨強弱を各通貨分取得する

    Returns
    -------
    dict[str, float]
      8通貨分の通貨強弱
      {"USD": 25.85, "EUR": -34.99, ...}
    None
      OHLCデーターに欠損があった場合通貨強弱を計算できない
    """

    dt = datetime.datetime.now(SERVER_TIMEZONE).replace(hour=0, minute=0, second=0, microsecond=0)
    utc_datetime = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond, UTC)
    day_start_timestamp = int(utc_datetime.timestamp())

    strength = {}
    for currency in CURRENCIES:
        strength[currency] = []

    v1 = {}
    v2 = {}

    # v1(起点価格)の用意
    for symbol in SYMBOLS:
        ohlc = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M5, day_start_timestamp, 1)
        if not ohlc:
            return None
        else:
            v1[symbol] = ohlc.tolist()[0][1]

    # v2(比較用価格)の用意
    for symbol in SYMBOLS:
        ohlc = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 1)
        if not ohlc:
            return None
        else:
            v2[symbol] = ohlc.tolist()[0][4]

    # v1は起点の価格、v2は現在時刻の価格
    EURUSD = getVal(v1["EURUSD"], v2["EURUSD"])
    USDJPY = getVal(v1["USDJPY"], v2["USDJPY"])
    USDCHF = getVal(v1["USDCHF"], v2["USDCHF"])
    GBPUSD = getVal(v1["GBPUSD"], v2["GBPUSD"])
    AUDUSD = getVal(v1["AUDUSD"], v2["AUDUSD"])
    USDCAD = getVal(v1["USDCAD"], v2["USDCAD"])
    NZDUSD = getVal(v1["NZDUSD"], v2["NZDUSD"])
    EURJPY = getValM(v1["EURUSD"], v2["EURUSD"], v1["USDJPY"], v2["USDJPY"])
    EURCHF = getValM(v1["EURUSD"], v2["EURUSD"], v1["USDCHF"], v2["USDCHF"])
    EURGBP = getValD(v1["EURUSD"], v2["EURUSD"], v1["GBPUSD"], v2["GBPUSD"])
    CHFJPY = getValD(v1["USDJPY"], v2["USDJPY"], v1["USDCHF"], v2["USDCHF"])
    GBPCHF = getValM(v1["GBPUSD"], v2["GBPUSD"], v1["USDCHF"], v2["USDCHF"])
    GBPJPY = getValM(v1["GBPUSD"], v2["GBPUSD"], v1["USDJPY"], v2["USDJPY"])
    AUDCHF = getValM(v1["AUDUSD"], v2["AUDUSD"], v1["USDCHF"], v2["USDCHF"])
    AUDJPY = getValM(v1["AUDUSD"], v2["AUDUSD"], v1["USDJPY"], v2["USDJPY"])
    AUDCAD = getValM(v1["AUDUSD"], v2["AUDUSD"], v1["USDCAD"], v2["USDCAD"])
    EURCAD = getValM(v1["EURUSD"], v2["EURUSD"], v1["USDCAD"], v2["USDCAD"])
    GBPCAD = getValM(v1["GBPUSD"], v2["GBPUSD"], v1["USDCAD"], v2["USDCAD"])
    GBPAUD = getValD(v1["GBPUSD"], v2["GBPUSD"], v1["AUDUSD"], v2["AUDUSD"])
    EURAUD = getValD(v1["EURUSD"], v2["EURUSD"], v1["AUDUSD"], v2["AUDUSD"])
    CADCHF = getValD(v1["USDCHF"], v2["USDCHF"], v1["USDCAD"], v2["USDCAD"])
    CADJPY = getValD(v1["USDJPY"], v2["USDJPY"], v1["USDCAD"], v2["USDCAD"])
    AUDNZD = getValD(v1["AUDUSD"], v2["AUDUSD"], v1["NZDUSD"], v2["NZDUSD"])
    EURNZD = getValD(v1["EURUSD"], v2["EURUSD"], v1["NZDUSD"], v2["NZDUSD"])
    GBPNZD = getValD(v1["GBPUSD"], v2["GBPUSD"], v1["NZDUSD"], v2["NZDUSD"])
    NZDCAD = getValM(v1["NZDUSD"], v2["NZDUSD"], v1["USDCAD"], v2["USDCAD"])
    NZDCHF = getValM(v1["NZDUSD"], v2["NZDUSD"], v1["USDCHF"], v2["USDCHF"])
    NZDJPY = getValM(v1["NZDUSD"], v2["NZDUSD"], v1["USDJPY"], v2["USDJPY"])

    # 各通貨の値の計算
    Pairs = 7

    # その時間における通貨ごとの通貨強弱
    values = {
        "EUR": (EURUSD + EURJPY + EURCHF + EURGBP + EURAUD + EURCAD + EURNZD) / Pairs,
        "USD": (-EURUSD + USDJPY + USDCHF - GBPUSD - AUDUSD + USDCAD - NZDUSD) / Pairs,
        "JPY": (-EURJPY - USDJPY - CHFJPY - GBPJPY - AUDJPY - CADJPY - NZDJPY) / Pairs,
        "CHF": (-EURCHF - USDCHF + CHFJPY - GBPCHF - AUDCHF - CADCHF - NZDCHF) / Pairs,
        "GBP": (-EURGBP + GBPUSD + GBPCHF + GBPJPY + GBPAUD + GBPCAD + GBPNZD) / Pairs,
        "AUD": (-EURAUD + AUDUSD + AUDJPY + AUDCHF - GBPAUD + AUDCAD + AUDNZD) / Pairs,
        "CAD": (-EURCAD - USDCAD + CADJPY + CADCHF - GBPCAD - AUDCAD - NZDCAD) / Pairs,
        "NZD": (-EURNZD + NZDUSD + NZDJPY + NZDCHF - GBPNZD + NZDCAD - AUDNZD) / Pairs
    }

    for currency, value in values.items():
        strength[currency] = value

    return strength


def getVal(v1, v2):
    if v2 == 0:
        return
    return math.log(v2 / v1) * 10000


def getValM(v1, v2, v3, v4):
    v1 = v1 * v3
    v2 = v2 * v4
    if v2 == 0:
        return
    return math.log(v2 / v1) * 10000


def getValD(v1, v2, v3, v4):
    if v3 == 0 or v4 == 0:
        return
    v1 = v1 / v3
    v2 = v2 / v4
    if v2 == 0:
        return
    return math.log(v2 / v1) * 10000
