import os


class GetOutOfLoop(Exception):
    pass


def ensure_dir(file_path):
    '''Make sure specified directory exists

    Arguments:
        file_path {string} -- Path for the directory

    Returns:
        bool -- Directory Created
    '''
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.mkdir(directory)
        return True
    return False


def is_number(num):
    '''Check if specified string is number

    Arguments:
        num {string} -- String to check

    Returns:
        bool -- Is Number
    '''
    try:
        _ = int(num)
        return True
    except GetOutOfLoop:
        return False
