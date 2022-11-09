import datetime

from config import SINCE, UNTIL, SERVER_TIMEZONE


def is_available_time() -> bool:
    """ 現在時刻が定数で定義しているエントリー対象時間内かどうか

    例: SINCE:8, UNTIL: 22の場合、8:00から21:55までTrueが返される

    Returns
    -------
    bool
        定数で定義しているエントリー対象時間内かどうか
    """

    since = datetime.time(SINCE, 0, 0)
    until = datetime.time(UNTIL, 0, 0)
    targetTime = datetime.datetime.now(SERVER_TIMEZONE).time()

    if SINCE < UNTIL:
        return since <= targetTime < until
    else:
        return targetTime < until or targetTime >= since


def is_DST() -> bool:
    """ サーバータイムゾーンが現在サマータイム期間中かどうか判定する

    Returns
    -------
    bool
        サーバータイムゾーンが現在サマータイム期間中かどうか
    """

    if datetime.datetime.now(SERVER_TIMEZONE).dst():
        return True

    return False


def is_open_market() -> bool:
    """ 現在外為市場がオープンしているかどうか判定する

    Returns
    -------
    bool
        現在外為市場がオープンしているかどうか
    """

    offset2 = datetime.timezone(datetime.timedelta(hours=2))
    offset3 = datetime.timezone(datetime.timedelta(hours=3))

    dt = offset3 if is_DST() else offset2

    # 土日チェック
    if dt.weekday() >= 5:
        return False

    # 元日チェック
    if dt.month == 1 and dt.day == 1:
        return False

    return True
