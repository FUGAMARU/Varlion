from pprint import pprint
import logging

from common_function import is_open_market, is_available_time, get_currency_strength, get_symbol, check_deviation, check_sma_state, get_direction
from mt5_api_function import send_order, is_order_done, get_sma, send_settlement
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
                    send_message(f"[#{order_result.order}] {symbol}を{direction}しました ({order_result.price} * {order_result.volume}Lots)", "ORDER")

                    logging.info(order_result)

                    logging.info(f"{k1}({v1}) vs {k2}({v2})")
                    send_message(f"{k1}({v1}) vs {k2}({v2})", "ORDER")
                    logging.info(pprint(gv.positions))
                else:
                    logging.error(f"{symbol}の{direction}に失敗しました code={order_result.retcode}, message={order_result.comment}")
                    logging.error(order_result)
                    send_message(f"{symbol}の{direction}に失敗しました code={order_result.retcode}, message={order_result.comment}", "ERROR")


def settlement() -> None:
    """ 保有ポジションがあれば決済を試行する """

    if not gv.positions:
        return

    for k in list(gv.positions.keys()):
        v = gv.positions[k]
        sma = get_sma(k)

        if (v["direction"] == "LONG" and sma[0] >= sma[1]) or (v["direction"] == "SHORT" and sma[0] <= sma[1]):  # SMAが反転していたら
            orderResult = send_settlement(k, v)

            if is_order_done(orderResult):
                del gv.positions[k]
                perpetuate_state()

                logging.info(f"[#{v['ticket']}] {k}の{v['direction']}を決済しました ({orderResult.price} * {orderResult.volume}Lots)")
                send_message(f"[#{v['ticket']}] {k}の{v['direction']}を決済しました ({orderResult.price} * {orderResult.volume}Lots)", "ORDER")
            else:
                logging.error(f"[#{v['ticket']}] {k}の{v['direction']}の決済に失敗しました code={orderResult.retcode}, message={orderResult.comment}")
                logging.error(orderResult)
                send_message(f"[#{v['ticket']}] {k}の{v['direction']}の決済に失敗しました code={orderResult.retcode}, message={orderResult.comment}", "ERROR")

            logging.info(pprint(gv.positions))
