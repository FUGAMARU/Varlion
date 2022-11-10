import datetime
import requests
import logging
import time
import json

from config import SINCE, UNTIL, SERVER_TIMEZONE, USE_EXTERNAL_SOURCE, SOUCE_URL
from constant import SYMBOLS, ROOT_DIR
from currency_strength import get_original_currency_strength
from message_control import send_message
from mt5_api_function import get_sma


def is_available_time() -> bool:
    """ 現在時刻が定数で定義しているエントリー対象時間内かどうか

    例: SINCE:8, UNTIL: 22の場合、8:00から21:55までTrueが返される

    Returns
    -------
    bool
        定数で定義しているエントリー対象時間内かどうか
    """

    since = datetime.time(SINCE, 0, 0)
    until = datetime.time(UNTIL, 0, 0)
    target_time = datetime.datetime.now(SERVER_TIMEZONE).time()

    if SINCE < UNTIL:
        return since <= target_time < until
    else:
        return target_time < until or target_time >= since


def is_DST() -> bool:
    """ サーバータイムゾーンが現在サマータイム期間中かどうか判定する

    Returns
    -------
    bool
        サーバータイムゾーンが現在サマータイム期間中かどうか
    """

    if datetime.datetime.now(SERVER_TIMEZONE).dst():
        return True

    return False


def is_open_market() -> bool:
    """ 現在外為市場がオープンしているかどうか判定する

    Returns
    -------
    bool
        現在外為市場がオープンしているかどうか
    """

    offset2 = datetime.timezone(datetime.timedelta(hours=2))
    offset3 = datetime.timezone(datetime.timedelta(hours=3))

    dt = offset3 if is_DST() else offset2

    # 土日チェック
    if dt.weekday() >= 5:
        return False

    # 元日チェック
    if dt.month == 1 and dt.day == 1:
        return False

    return True


def get_currency_strength() -> dict[str, float] | None:
    """ 当日分の現在における通貨強弱を各通貨分取得する

    Returns
    -------
    Dict[str, float]
        最も新しい通貨ごとの通貨強弱データー
        例: {"USD": 15, "EUR": 20, ...}
    None
        独自に通貨強弱を計算する時にOHLCデーターの欠損があった場合
    """

    if USE_EXTERNAL_SOURCE:
        currency_strength = {}

        while True:
            try:
                response = requests.get(SOUCE_URL)
                currency_strength_data = response.json()

                now = int(time.time())
                latest_timestamp = int(currency_strength_data[0]["values"][-1][0] * 0.001)

                if abs(latest_timestamp - now) <= 60:  # 取れたデーターが新しいものか
                    for currency in currency_strength_data:
                        currency_strength[currency["key"]] = currency["values"][-1][1]
                    break
                else:
                    time.sleep(3)
            except:
                logging.error("通貨強弱データーの処理エラーが発生しました")
                logging.error("3秒後に再試行します")
                send_message("通貨強弱データーの処理エラーが発生しました")
                send_message("3秒後に再試行します")
                time.sleep(3)
                continue

        return currency_strength
    else:
        return get_original_currency_strength()


def get_symbol(cur1: str, cur2: str) -> str:
    """通貨と通貨からシンボルを返す

    Parameters
    ----------
    cur1: str
        1つ目の通貨
    cur2: str
        2つ目の通貨

    Returns
    -------
    str
        シンボル
    """

    return cur1 + cur2 if cur1 + cur2 in SYMBOLS else cur2 + cur1


def check_deviation(cur1: str, cur2: str, val1: str, val2: str) -> bool:
    """ エントリー可能な乖離条件を満たしているか判定する

    Parameters
    ----------
    cur1: str
        1つ目の通貨
    cur2: str
        2つ目の通貨
    val1: str
        1つ目の通貨の通貨強弱
    val2: str
        2つ目の通貨の通貨強弱

    Returns
    -------
    bool
        エントリー可能な乖離条件を満たしているかどうか
    """

    with open(f"{ROOT_DIR}/deviation.json", "r") as file:
        deviations = json.load(file)

        if val1 > val2:
            return val1 - val2 >= deviations[cur1] and val1 - val2 >= deviations[cur2]
        else:
            return val2 - val1 >= deviations[cur1] and val2 - val1 >= deviations[cur2]


def get_direction(cur1: str, cur2: str, cur1_val: float, cur2_val: float, contrary: bool) -> dict[str, str]:
    """ 通貨とその通貨強弱指数から取るべきポジションを判定する

    Parameters
    ----------
    cur1: str
        1つ目の通貨
    cur2: str
        2つ目の通貨
    cur1_val: float
        1つ目の通貨の通貨強弱
    cur2_val: float
        2つ目の通貨の通貨強弱
    contrary: bool
        逆張りするかどうか

    Returns
    -------
    Dict[str, str]
        シンボルと取るべきポジション("LONG" or "SHORT")
    """

    if cur1_val > cur2_val and cur1 + cur2 in SYMBOLS:
        return {"symbol": get_symbol(cur1, cur2), "position": "SHORT" if contrary else "LONG"}
    elif cur1_val > cur2_val and cur1 + cur2 not in SYMBOLS:
        return {"symbol": get_symbol(cur1, cur2), "position": "LONG" if contrary else "SHORT"}
    elif cur2_val > cur1_val and cur1 + cur2 in SYMBOLS:
        return {"symbol": get_symbol(cur1, cur2), "position": "LONG" if contrary else "SHORT"}
    elif cur2_val > cur1_val and cur1 + cur2 not in SYMBOLS:
        return {"symbol": get_symbol(cur1, cur2), "position": "SHORT" if contrary else "LONG"}


def check_sma_state(cur1: str, cur2: str, val1: float, val2: float) -> bool:
    """ SMAが通貨強弱に沿った状態(ゴールデンクロス・デッドクロス)かどうかを順張り基準で判定する

    Parameters
    ----------
    cur1: str
        通貨1
    cur2: str
        通貨2
    val1: float
        通貨1の通貨強弱
    val2: float
        通貨2の通貨強弱

    Returns
    -------
    bool:
        SMAが通貨強弱に沿った状態であるかどうか (通貨強弱が全く同じ値の場合は無条件でFalseを返す)
    """

    sma = get_sma(get_symbol(cur1, cur2))
    direction = get_direction(cur1, cur2, val1, val2, False)

    return (direction["position"] == "LONG" and sma[0] >= sma[1]) or (direction["position"] == "SHORT" and sma[0] <= sma[1])
