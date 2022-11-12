import MetaTrader5 as mt5
import logging

from config import SHORT_SMA, LONG_SMA, LOT, STOPLOSS, FILLING_TYPE
from file_operation import perpetuate_state
from message_control import send_message
import gv


def get_positions() -> list[str] | None:
    """ 保有中ポジションのシンボル一覧をMT5から取得する

    Returns
    -------
    list[str]:
    保有中ポジションのシンボル一覧
    None:
    保有中ポジションが無い場合
    """

    positions = mt5.positions_get()

    if not positions:
        return None

    symbols = []
    for position in positions:
        symbols.append(position.symbol)

    return symbols


def check_losscut_executed() -> None:
    """ 損切りが実行されたかチェックする

        損切されていた場合、グローバル変数と所有中ポジション情報を同期し、LINE Notifyでメッセージを送信する
    """

    mt5_positions = get_positions()

    if not mt5_positions:
        return

    diff = list(set(mt5_positions) ^ set(gv.positions))

    if not diff:
        return

    for symbol in diff:
        if symbol in list(gv.positions.keys()):
            del gv.positions[symbol]
            perpetuate_state()

            logging.info(f"{symbol}が損切り決済されました")
            send_message(f"{symbol}が損切り決済されました", "STOPLOSS")


def get_sma(symbol: str) -> list[float]:
    """ 定数で定義されている期間のSMAを算出する(現在値ではなく直近の確定足のもの)

    Parameters
    ----------
    symbol: str
        通貨ペア

    Returns
    -------
    List[float]
        [dur1から算出したSMA, dur2から算出したSMA]
    """

    rates1 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, SHORT_SMA + 1)
    rates2 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, LONG_SMA + 1)

    total1 = total2 = 0.0

    for i in range(SHORT_SMA):
        total1 += rates1[i]["close"]

    for i in range(LONG_SMA):
        total2 += rates2[i]["close"]

    sma1, sma2 = total1 / SHORT_SMA, total2 / LONG_SMA

    return [sma1, sma2]


def get_current_rate(symbol: str, rate_type: str) -> float:
    """ 指定したシンボルのBidレートもしくはAskレートを取得する

    Parameters
    ----------
    symbol: str
        シンボル
    rate_type: str
        Bidレートを取得するのかAskレートを取得するのか ("BID" or "ASK")

    return
    ------
        float
        指定されたシンボルのBidレート、もしくはAskレート
    """

    return mt5.symbol_info_tick(symbol).bid if rate_type == "BID" else mt5.symbol_info_tick(symbol).ask


def get_spread(symbol: str) -> int:
    """ 指定したシンボルの現在のスプレッドを取得する

    Parameters
    ----------
    symbol: str
        シンボル

    Returns
    -------
    int
        スプレッド(単位: points)
    """

    return mt5.symbol_info(symbol).spread


def send_order(symbol: str, direction: str) -> dict[str, any]:
    """ エントリーして損切りを置く

    Parameters
    ----------
    symbol: str
        シンボル
    direction: str
        エントリー方向 ("LONG" or "SHORT")

    Returns
    -------
    dict[str, any]
        MqlTradeResult型の辞書 (https://www.mql5.com/ja/docs/constants/structures/mqltraderesult)
    """

    current_rate = get_current_rate(symbol, "ASK") if direction == "LONG" else get_current_rate(symbol, "BID")
    spread = get_spread(symbol)

    # 損切りレートの算出
    sl: float
    if "JPY" in symbol:
        sl = current_rate - (STOPLOSS + spread) * 0.001 if direction == "LONG" else current_rate + (STOPLOSS + spread) * 0.001
    else:
        sl = current_rate - (STOPLOSS + spread) * 0.00001 if direction == "LONG" else current_rate + (STOPLOSS + spread) * 0.00001

    res = mt5.order_send({
        "action": mt5.TRADE_ACTION_DEAL,  # 成行注文
        "magic": 20707000,  # マジックナンバー(用途不明だけど一応指定)
        "symbol": symbol,  # シンボル
        "price": current_rate,
        "volume": LOT,  # ロット数
        "sl": sl,  # 損切りレート
        "deviation": 100,  # 許容スリッページ(ポイント)
        "type": mt5.ORDER_TYPE_BUY if direction == "LONG" else mt5.ORDER_TYPE_SELL,  # エントリー方向
        "type_filling": mt5.ORDER_FILLING_IOC if FILLING_TYPE == "IOC" else mt5.ORDER_FILLING_FOK,  # 注文タイプ
        "type_time": mt5.ORDER_TIME_GTC  # 待機注文の有効期限を設定しない
    })

    return res


def send_settlement(symbol: str, position_info: dict[str, any]) -> dict[str, any]:
    """決済注文を出す

    Parameters
    ----------
    symbol:
        シンボル
    position_info: dict[str, any]
        ポジション情報

    Returns
    -------
    dict[str, any]
        MqlTradeResult型の辞書 (https://www.mql5.com/ja/docs/constants/structures/mqltraderesult)
    """

    order_type: any
    price: float
    if position_info["direction"] == "LONG":
        order_type = mt5.ORDER_TYPE_SELL
        price = get_current_rate(symbol, "BID")
    else:
        order_type = mt5.ORDER_TYPE_BUY
        price = get_current_rate(symbol, "ASK")

    res = mt5.order_send({
        "action": mt5.TRADE_ACTION_DEAL,  # 成行注文
        "magic": 20707000,  # マジックナンバー(用途不明だけど一応指定)
        "position": position_info["ticket"],  # チケット番号
        "symbol": symbol,
        "price": price,  # 注文価格(成行なのに指定しないといけない理由は不明)
        "volume": position_info["lot"],  # ロット数
        "deviation": 100,  # 許容スリッページ(ポイント)
        "type": order_type,  # 決済注文
        "type_filling": mt5.ORDER_FILLING_IOC if FILLING_TYPE == "IOC" else mt5.ORDER_FILLING_FOK  # 注文タイプ
    })

    return res


def is_order_done(order_result: tuple) -> bool:
    """ オーダー結果のデーターを元に、オーダーが正常に完了したか確認する

    Parameters
    ----------
    order_result: tuple
        MqlTradeResult(https://www.mql5.com/ja/docs/constants/structures/mqltraderesult)

    Returns
    -------
    bool
        オーダーが正常に完了したかどうか
    """

    return order_result.retcode == mt5.TRADE_RETCODE_DONE
