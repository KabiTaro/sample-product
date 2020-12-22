from datetime import datetime, timedelta

from pytz import utc


def iso_format_datetime_str(delta_days: int = 0) -> str:
    """
    identityAPIv2.0のレスポンス内のexpires(トークン発行日時の翌日)を再現する
    ISO 8601形式の明日の日時(utc)を文字列で返す

    Args:
        delta_days (int, optional): 日差. Defaults to 0.

    Returns:
        str: ISO 8601形式の明日の日時
    """
    aware_datetime = datetime.now(tz=utc)+timedelta(days=delta_days)

    return aware_datetime.isoformat().split('.')[0]+'Z'


TEST_IMAGE = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB0AAAA'\
    'eCAYAAADQBxWhAAAAo0lEQVRIS+2VQRaAIAhE4/6HpufCHhI6JNEm2qIO/BmNmJmPj'\
    'z8q0UzihXdKl4iu2m7wB7z9QM9hba1nndX9zVM5id4gRV4V9aR2JeihtZVeNCWs6xf'\
    'Jwqu9Q4c2Wksa1jOIEorqIVErndqzmYePJ/WESa+xmpldqa0goaZQglNEu6eyueGOZ'\
    '/xPke9pk64sKFEU0FC98Ibwoc2FFxEK1f+D9wSFTMKnZLSOqwAAAABJRU5ErkJggg=='
