import MetaTrader5 as mt5
import logging

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
            send_message(f"{symbol}が損切り決済されました")
