import json

from constant import ROOT_DIR


def get_config() -> dict[str, str | int]:
    """ 設定ファイルから値を取得する
    Returns
    -------
    dict[str, str | int]
        設定
    """
    with open(f"{ROOT_DIR}/config.json") as file:
        return json.load(file)
