import schedule
import time
import datetime

from constant import JST
from mt5_api_function import check_losscut_executed
from common_function import is_available_time
from file_operation import perpetuate_state
from order_action import entry, settlement
import gv


def main() -> None:
    def every1sec() -> None:
        dt = datetime.datetime.now(JST)
        minute, second = dt.minute, dt.second

        # 5秒ごとの処理
        if second % 5 == 0:
            check_losscut_executed()

        # 5分ごとの処理
        if minute % 5 == 0 and minute != gv.lastProcessed:
            print(f"[{dt}] 仕事中！ Σ( ºωº )")

            # 範囲時間外に前営業日にエントリーした通貨ペアの履歴を消す
            if not is_available_time() and gv.entried:
                gv.entried = []
                perpetuate_state()

            entry()

            # 決済用処理(SMAの反転チェック)
            # if gv.positions:  # 持っているポジションがあるか -> (!Todo) order_action側に判定ロジックを移動する
            settlement()

            gv.lastProcessed = minute

    # スケジューラー
    schedule.every(1).seconds.do(every1sec)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
