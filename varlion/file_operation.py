import json

from constant import ROOT_DIR
import gv


def perpetuate_state() -> None:
    """ ポジションの保有状況を永続化データーとしてファイルに出力する """

    with open(f"{ROOT_DIR}/persistence.json", "w") as file:
        dumpData = {"entried": gv.entried, "positions": gv.positions}
        json.dump(dumpData, file, indent=4)
