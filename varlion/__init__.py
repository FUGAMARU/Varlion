import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

from pyfiglet import Figlet
import logging
from logging import (StreamHandler, FileHandler, Formatter, basicConfig, INFO)
import MetaTrader5 as mt5

from constant import ROOT_DIR
from config import ACCOUNT_NUMBER, PASSWORD, SERVER
from message_control import send_message

print(Figlet(font="slant").renderText("Varlion"))

# ロギング設定
LOG_LEVEL = INFO

stream_handler = StreamHandler()
stream_handler.setLevel(LOG_LEVEL)
stream_handler.setFormatter(Formatter("[%(asctime)s]:%(levelname)s:%(message)s"))

file_handler = FileHandler(f"{ROOT_DIR}/events.log")
stream_handler.setLevel(LOG_LEVEL)
file_handler.setFormatter(Formatter("[%(asctime)s]:%(levelname)s:%(message)s"))

basicConfig(level=LOG_LEVEL, handlers=[stream_handler, file_handler])

if not mt5.initialize():
    logging.error(f"初期化に失敗しました  エラー: {mt5.last_error()}")
    quit()

logging.info(f"MT5(v{mt5.__version__})との接続に成功しました")

authorized = mt5.login(ACCOUNT_NUMBER, password=PASSWORD, server=SERVER)

if not authorized:
    logging.error("ユーザー認証に失敗しました")
    quit()

logging.info(f"ユーザー認証に成功しました(接続先サーバー: {SERVER})")
logging.info("Varlionが正常に起動しました")
logging.info("モニタリングを開始します")

send_message("Varlionが起動しました")
