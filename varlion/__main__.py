import schedule
import time
import datetime

from constant import JST
from mt5_api_function import check_losscut_executed
from common_function import is_available_time
from file_operation import perpetuate_state
from order_action import entry, settlement
from message_control import send_message
import gv


def main() -> None:
    def every1sec() -> None:
        dt = datetime.datetime.now(JST)
        minute, second = dt.minute, dt.second

        # 5秒ごとの処理
        if second % 5 == 0:
            check_losscut_executed()

        # 5分ごとの処理
        if minute % 5 == 0 and minute != gv.lastProcessed5m:
            print(f"[{dt}] 仕事中！ Σ( ºωº )")

            # 範囲時間外に前営業日にエントリーした通貨ペアの履歴を消す
            if not is_available_time() and gv.entried:
                gv.entried = []
                perpetuate_state()

            entry()

            settlement()

            gv.lastProcessed5m = minute

        # 1時間ごとの処理
        if minute == 0 and minute != gv.lastProcessed1h:
            # 現在のポジション保有状況を送信する
            send_message(f"本日の累計エントリー回数: {len(gv.entried)}", "STATUS")

    # スケジューラー
    schedule.every(1).seconds.do(every1sec)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
