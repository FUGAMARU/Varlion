import schedule
import time
import datetime

from constant import JST
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
            # エントリーや決済など...

            gv.lastProcessed = minute

    # スケジューラー
    schedule.every(1).seconds.do(every1sec)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
