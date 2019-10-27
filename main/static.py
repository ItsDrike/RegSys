import hashlib
import os
import re


class GetOutOfLoop(Exception):
    pass


class RegistrationError(Exception):
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


def readable_permission(permlvl):
    val = 'unknown'
    if permlvl == 3:
        val = 'user'
    elif permlvl == 2:
        val = 'admin'
    elif permlvl == 1:
        val = 'superadmin'
    elif permlvl == 0:
        val = 'developer'
    return val


def check_password_requirements(pw):
    '''Check if password meets the requirements

    Arguments:
        pw {string} -- Plain password

    Returns:
        bool -- Password meets requirements
    '''
    rules = [
        # must have at least one uppercase
        lambda s: any(x.isupper() for x in s),
        # must have at least one lowercase
        lambda s: any(x.islower() for x in s),
        lambda s: any(x.isdigit()
                      for x in s),  # must have at least one digit
        # must be at least 7 characters
        lambda s: len(s) >= 7
    ]
    if all(rule(pw) for rule in rules):
        return True
    else:
        return False


def check_mail(mail):
    '''Check the email format

    Arguments:
        mail {string} -- E-Mail Address

    Returns:
        bool -- Valid E-Mail Format
    '''
    if re.match(r'[^@]+@[^@]+\.[^@]', mail):
        return True
    else:
        return False


def encrypt(pword):
    '''Encrypt password using hashlibs SHA224 hash

    Arguments:
        pword {string} -- Plain password

    Returns:
        string -- Encrypted password
    '''
    return hashlib.sha224(pword.encode('UTF-8')).hexdigest()
