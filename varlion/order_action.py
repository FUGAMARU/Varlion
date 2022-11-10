from pprint import pprint
import logging

from common_function import is_open_market, is_available_time, get_currency_strength, get_symbol, check_deviation, check_sma_state, get_direction
from mt5_api_function import send_order, is_order_done
from message_control import send_message
from file_operation import perpetuate_state
import gv


def entry() -> None:
    """ オーダーを試行する """

    if not is_open_market() or not is_available_time():
        return

    currency_strength = get_currency_strength()
    for k1, v1 in currency_strength.items():
        for k2, v2 in currency_strength.items():
            if k1 == k2 or v1 == v2:
                continue

            symbol = get_symbol(k1, k2)

            is_not_entried = symbol not in gv.positions  # 既に保有中ポジションがあるシンボルでないか
            is_not_entried_today = symbol not in gv.entried  # まだ今日エントリーしていない通貨ペアか
            is_discrepancy = check_deviation(k1, k2, v1, v2)  # 乖離基準を満たしているか
            is_ordered_sma = check_sma_state(k1, k2, v1, v2)  # SMAが通貨強弱に沿った並びをしているか

            if is_not_entried and is_not_entried_today and is_discrepancy and is_ordered_sma:
                direction = get_direction(k1, k2, v1, v2, True)

                order_result = send_order(symbol, direction)

                if is_order_done(order_result):
                    gv.positions[symbol] = {"ticket": order_result.order, "lot": order_result.volume, "rate": order_result.price, "direction": direction}
                    gv.entried.append(symbol)
                    perpetuate_state()

                    logging.info(f"[#{order_result.order}] {symbol}を{direction}しました ({order_result.price} * {order_result.volume}Lots)")
                    send_message(f"[#{order_result.order}] {symbol}を{direction}しました ({order_result.price} * {order_result.volume}Lots)")

                    logging.info(order_result)
                else:
                    logging.error(f"{symbol}の{direction}に失敗しました code={order_result.retcode}, message={order_result.comment}")
                    logging.error(order_result)
                    send_message(f"{symbol}の{direction}に失敗しました code={order_result.retcode}, message={order_result.comment}")

                    logging.info(f"{k1}({v1}) vs {k2}({v2})")
                    send_message(f"{k1}({v1}) vs {k2}({v2})")
                    logging.info(pprint(gv.positions))


def settlement() -> None:
    """ 保有ポジションがあれば決済を試行する """
    print("決済関連処理")
