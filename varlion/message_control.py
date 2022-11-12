import requests

from config import LINE_NOTIFY_TOKEN, LINE_NOTIFY_PREFIX, ALLOWED_MESSAGE_TYPES


def send_message(message: str, message_type: str) -> None:
    """ LINE Notifyでメッセージを送信する

    Parameters
    ----------
    message: str
        送信するメッセージ
    message_type: str
        メッセージタイプ
    """

    if message_type in ALLOWED_MESSAGE_TYPES:
        headers = {"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"}
        data = {"message": f"[{LINE_NOTIFY_PREFIX}] {message}"}
        requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)
