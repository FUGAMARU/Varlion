import requests

from config import LINE_NOTIFY_TOKEN, LINE_NOTIFY_PREFIX


def send_message(message: str) -> None:
    """ LINE Notifyでメッセージを送信する

    Parameters
    ----------
    message: str
        送信するメッセージ
    """

    headers = {"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"}
    data = {"message": f"[{LINE_NOTIFY_PREFIX}] {message}"}
    requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)
