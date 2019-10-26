from importlib import import_module

logger = import_module('RegSys').logger


def show_menu(perm):
    '''Show Menu for user with specified permission level

    Arguments:
        perm {int} -- Permission level
    '''
    # Developer Menu
    if perm == 0:
        logger.debug('Showing maxlevel options')
        print(f' ->1: Create new user')
        print(f' ->2: Remove existing user')
        print(f' ->3: Edit existing user')
        print(f' ->4: Change your E-Mail address')
        print(f' ->5: Change your password')
        print(f' ->6: Python DeveloperShell')
        print(f' ->7: Log-out')
    # SuperAdmin Menu
    elif perm == 1:
        logger.debug('Showing superadmin options')
        print(f' ->1: Create new user')
        print(f' ->2: Remove existing user')
        print(f' ->3: Edit existing user')
        print(f' ->4: Change your E-Mail address')
        print(f' ->5: Change your password')
        print(f' ->6: Log-out')
    # Admin Menu
    elif perm == 2:
        logger.debug('Showing admin options')
        print(f' ->1: Create new user')
        print(f' ->2: Remove existing user')
        print(f' ->3: Edit existing user')
        print(f' ->4: Change your E-Mail address')
        print(f' ->5: Change your password')
        print(f' ->6: Log-out')
    # User Menu
    elif perm == 3:
        logger.debug('Showing user options')
        print(f' ->1: Change E-Mail address')
        print(f' ->2: Change password')
        print(f' ->3: Log-out')
