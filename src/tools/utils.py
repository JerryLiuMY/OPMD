from datetime import datetime


def get_now():
    now = datetime.now().strftime('%Y%m%d-%H%M%S')
    return now
