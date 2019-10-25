import os
from pathlib import Path
from importlib import import_module


def ensure_dir(file_path, LOG_FILE='logs/logfile.log'):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.mkdir(directory)

    if not Path(file_path).is_file():
        with open(LOG_FILE, 'w'):
            pass


def is_number(num):
    GetOutOfLoop = import_module('RegSys.py').GetOutOfLoop
    try:
        _ = int(num)
        return True
    except GetOutOfLoop:
        return False
