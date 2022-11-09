import schedule
import time
import datetime

from constant import JST
from file_operation import perpetuate_state
from order_action import entry, settlement
from common_function import is_available_time
import gv


def main() -> None:
    def every1sec() -> None:
        dt = datetime.datetime.now(JST)
        minute, second = dt.minute, dt.second

        # 5秒ごとの処理
        if second % 5 == 0:
            print("5秒ごとに損切りに引っかかったかチェックする")

        # 5分ごとの処理
        if minute % 5 == 0 and minute != gv.lastProcessed:
            print(f"[{dt}] 仕事中！ Σ( ºωº )")

            # 範囲時間外に前営業日にエントリーした通貨ペアの履歴を消す
            if not is_available_time() and gv.entried:
                gv.entried = []
                perpetuate_state()

            # 新規エントリー用処理
            # if function.isOnTime(int(time.time())) and function.isWeekday(int(time.time())):  # 指定時間内かつマーケット平日かどうか  -> (!Todo) order_action側に判定ロジックを移動する
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
