import os
from pathlib import Path


class GetOutOfLoop(Exception):
    pass


def ensure_dir(file_path, LOG_FILE='logs/logfile.log'):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.mkdir(directory)

    if not Path(file_path).is_file():
        with open(LOG_FILE, 'w'):
            pass


def is_number(num):
    try:
        _ = int(num)
        return True
    except GetOutOfLoop:
        return False