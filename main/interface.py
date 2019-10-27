from os import system
import sys
from importlib import import_module
from pword_mod import get_pword

logger = import_module('RegSys').logger
static = import_module('RegSys').static
database = import_module('RegSys').database


def welcome_screen():
    '''Prints the main interface

    Returns:
        string -- User response (choice)
    '''
    system('cls')
    print('Welcome to RegSys Software, created by Koumakpet <koumakpet@hexadynamic.com>')
    print(' ->Login:            1')
    print(' ->Register:         2')
    print(' ->Exit/Go back:     *')
    main_prompt = input('\nWhat do you want to do?: ')
    return main_prompt.lower()


def invalid_choice(clear=True):
    print('Invalid choice')
    if clear:
        input('Press Enter to continue..')
        system('cls')


def invalid_password_requirements(clear=True):
    logger.debug('password requirements not met')
    print(
        '\nPassword does not meet requirements. Must contain at least:')
    print(
        '  1 Uppercase letter \n  1 Lowercase letter \n  1 Number \n  Minimum length of 7 characters')
    input('Press Enter to continue..')
    if clear:
        system('cls')


def handle_exception(exception, clear=True):
    print('\nProgram failed, send this error message to developer:')
    print(f' ->  Error: {exception}')
    input('Press Enter to continue..')
    if clear:
        system('cls')


def handle_user_abort(clear=True):
    logger.debug('User-Aborted')
    input('Action aborted, Press Enter to continue..')
    if clear:
        system('cls')


def handle_exit():
    logger.debug('choice: END (*)')
    logger.info('Program ended by user')
    input('Press enter to end program..')


def user_login(clear=True, usr=None, DATABASE='database.db'):
    '''User Interface for logging in

    Keyword Arguments:
        clear {bool} -- Clear screen (default: {True})
        usr {string} -- Username (default: {None})
        DATABASE {string} -- Path to database file (default: {'database.db'})

    Returns:
        LoggedUser -- Logged User class
    '''
    logger.trace('logging-in process started')
    if clear:
        system('cls')
    print('-Login-')
    if not usr:
        usr_name = input('Enter your username: ').lower()
        if usr_name == '*':
            print('Abort')
            logger.trace('logging-in aborted')
            return None
        pword = get_pword('State your password: ')
    else:
        usr_name = usr
        pword = get_pword(f'Enter password for {usr}')
    pword_enc = static.encrypt(pword)

    if database.account_exists(usr_name, pword_enc, DATABASE):
        logger.trace('user information confirmed, user exists')
        logger.info(f'user {usr_name} logged.')
        print('\nLogged in successfully')
        input('Press Enter to continue..')
        system('cls')
        return LoggedUser(usr_name)
    else:
        # No such user
        logger.debug('username or password incorrect')
        print('\nInvalid username or password')
        input('Press Enter to continue..')
        system('cls')
        if not usr:
            user_login()
        else:
            return None


def user_register(clear=True, mail=None, usr=None):
    '''User Interface for registering new user

    Keyword Arguments:
        clear {bool} -- Clear screen (default: {True})
        mail {string} -- E-Mail address (default: {None})
        usr {string} -- Username (default: {None})

    Returns:
        bool -- Successfull registration
    '''
    logger.trace('registration process started')
    if clear:
        system('cls')
    print('-Register-')
    if not mail:
        email = input('Enter your email address: ').lower()
        if email == '*':
            logger.info('registration aborted')
            return False
        if not static.check_mail(email):
            logger.debug(f'Email format {mail} incorrect')
            print('\nEmail format is invalid (___@___.___)')
            input('Press Enter to continue..')
            return user_register(clear, usr=usr)
        else:
            logger.trace(f'Email format {mail} correct')
    else:
        print(f'E-Mail Address: {mail}')
        email = mail

    if not usr:
        usr_name = input('Enter your new username: ').lower()
        if not database.username_aviable(usr_name):
            logger.debug('registration username invalid (taken)')
            print('\nThis username is not available')
            input('Press Enter to continue..')
            return user_register(clear, mail=email)
        else:
            logger.debug('registration username valid')
    else:
        print(f'Username: {usr}')
        usr_name = usr

    pword = get_pword('Enter password: ')
    pword_rep = get_pword('Re-Enter password: ')
    if pword == pword_rep:
        logger.trace('password match confirmed')
        if static.check_password_requirements(pword):
            logger.trace('password requirements confirmed')
            database.register_user(email, usr_name, static.encrypt(pword), 3)
            logger.info(
                'Registered new user, name: {}'.format(usr_name))
            print('\nRegistered successfully')
            input('Press Enter to continue...')
            return True
        else:
            invalid_password_requirements(clear)
            return user_register(clear, mail=email, usr=usr_name)
    else:
        # In case passwords does not match
        logger.debug('passwords does not match')
        print('\nPasswords does not match')
        input('Press Enter to continue..')
        return user_register(clear, mail=email, usr=usr_name)


def dev_shell():
    try:
        while True:
            system('cls')
            print('-Python shell-')
            print(
                'Developer access (enter direct python commands)\n')
            print(f'Python {sys.version}')
            print('Type "help" for more information')
            while True:
                inp = input('>>>')
                if inp.lower() != 'exit' and inp.lower() != 'help':
                    logger.info(
                        'Python DeveloperShell: {}', inp)
                    try:
                        exec(inp)
                    except Exception as e:
                        print('  Exception handler -> Error:')
                        print(f'    Error: {e}')
                        logger.warning(
                            'Python DeveloperShell returned Error -> {}', e)
                elif inp.lower() == 'help':
                    logger.debug('Python DeveloperShell help')
                    system('cls')
                    print('-Help-\n')
                    print('This is a python developer shell')
                    print(
                        'You can execute direct python commands into program')
                    print(
                        'Warning: executing wrong commands can break this instance of the program')
                    print(
                        'If you don\'t know what are you doing, please exit the developer shell')
                    print(
                        '-------------------------------------------------------------------------')
                    print('Type \'exit\' to exit developer shell')
                    inp = input(
                        '\nPress enter to return to developer shell\n')
                    if inp.lower() == 'exit':
                        logger.debug(
                            'Python DeveloperShell exit (in help)')
                        return True
                    else:
                        break
                else:
                    logger.debug('Python DeveloperShell exit')
                    raise static.GetOutOfLoop
            else:
                continue
    except static.GetOutOfLoop:
        return False


class LoggedUser:
    def __init__(self, username, clear=True):
        self.username = username
        self.permission = database.get_permissions(self.username)
        self.perm_readable = static.readable_permission(self.permission)
        self.email = database.get_mail(self.username)
        self.password = database.get_pass(self.username)
        logger.debug(f'Logged as {self.username}')
        if clear:
            system('cls')

    def show_menu(self, clear=True, perm=None, get_inputs=True):
        '''Show Menu for user with specified permission level

        Keyword Arguments:
            perm {int} -- Temporal permission level (default: {None})'''
        if clear:
            system('cls')
        print(f'-Welcome {self.username}-\n')
        print(f'(Your current E-Mail: {self.email})')
        if perm is not None or self.permission > 3 or self.permission <= 0:
            if perm is None:
                perm = 3
            print(
                f'(Your permission level: Temporal {static.readable_permission(perm)} - Contact developer for more info or create new account.)')
        else:
            perm = self.permission
            print(f'(Your permission level: {self.perm_readable})')
        print(f'(Your Encrypted password: {self.password})\n')

        # Developer Menu
        if perm == 0:
            logger.debug('Showing maxlevel options')
            print(f' ->1: Python DeveloperShell')
            print(f' ->2: Create new user')
            print(f' ->3: Remove existing user')
            print(f' ->4: Edit existing user')
            print(f' ->5: Change your E-Mail address')
            print(f' ->6: Change your password')
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

        if get_inputs:
            return self.get_user_inputs(perm, from_menu=True)
        else:
            return None

    def get_user_inputs(self, perms=None, from_menu=False):
        '''[summary]

        Keyword Arguments:
            perm {int} -- Temporal permission level (default: {None})

        Returns:
            string  -- Action chosen
        '''
        if perms:
            perm = perms
        else:
            perm = self.permission
        logger.trace('Choosing from options')
        action = input('\nEnter action number: ')
        logger.trace(f'action choosed: {action}, perm level: {perm}')
        if action != '*':
            returnlist = [
                # Developer
                {
                    '7': 'logout',
                    '6': 'passchange',
                    '5': 'mailchange',
                    '4': 'edituser',
                    '3': 'removeuser',
                    '2': 'createuser',
                    '1': 'devshell'
                },
                # SuperAdmin
                {
                    '6': 'logout',
                    '5': 'passchange',
                    '4': 'mailchange',
                    '3': 'edituser',
                    '2': 'removeuser',
                    '1': 'createuser'
                },
                # Admin
                {
                    '6': 'logout',
                    '5': 'passchange',
                    '4': 'mailchange',
                    '3': 'edituser',
                    '2': 'removeuser',
                    '1': 'createuser'
                },
                # User
                {
                    '3': 'logout',
                    '2': 'passchange',
                    '1': 'mailchange',
                }
            ]
            try:
                return_val = returnlist[perm][action]
                logger.debug(f'User input interpreted as: {return_val}')
            except KeyError:
                if from_menu:
                    invalid_choice(clear=True)
                    return self.show_menu(perm=perms, get_inputs=True)
                else:
                    invalid_choice(clear=False)
                    return self.get_user_inputs(perms=perms, from_menu=False)
            else:
                return return_val
        else:
            return 'logout'

    def change_password(self, clear=True, override=False):
        logger.debug(f'trying to change password of {self.username} (self)')
        if clear:
            system('cls')
        print('-Change password-')

        if not override:
            inp = input(
                f'Hello {self.username}, do you want to change your password? (Y/N): ').lower()
        else:
            logger.trace('Overriding confirmation prompt')
            inp = 'y'

        if inp == 'y':
            logger.trace('Confirmation successful')
            if not override:
                old_pass = static.encrypt(
                    get_pword('Enter your current password: '))
            else:
                logger.trace('Overriding old_pass entry')
                old_pass = self.password

            if old_pass == self.password:
                logger.trace('Old password is correct (or override is ON)')
                new_pass = get_pword('Enter new password: ')
                new_pass2 = get_pword('Re-Enter new password: ')
                if new_pass == new_pass2:
                    logger.debug('New passwords are matching')
                    if static.check_password_requirements(new_pass):
                        logger.debug('Password requirements are met')
                        database.remove_user(self.username)
                        logger.info(
                            f'User {self.username} Unregistered (to change password)')
                        enc_pass = static.encrypt(new_pass)
                        database.register_user(
                            self.email, self.username, enc_pass, self.permission)
                        self.password = enc_pass
                        logger.info(
                            f'User {self.username} was registered with new password')
                        logger.debug(
                            f'New encrypted password of {self.username} is: {self.password}')
                        print('\nPassword has been changed successfully')
                        input('Press Enter to continue..')
                        if clear:
                            system('cls')
                        return True
                    else:
                        invalid_password_requirements(clear)
                        self.change_password(clear=clear, override=True)
                        logger.debug(
                            'Restarting with override (yes prompt and old pass entry)')
                else:
                    logger.debug('Passwords are not matching')
                    print('\nPasswords are not matching')
                    input('Press any key to continue..')
                    logger.debug(
                        'Restarting with override (yes prompt and old pass entry)')
                    self.change_password(clear=clear, override=True)
            else:
                logger.debug('Current password incorrect')
                print('\nYour password is incorrect (first, enter your old password)')
                input('Press Enter to continue..')
                return self.change_password(clear=clear, override=False)
        else:
            handle_user_abort()
            return False

    def remove_user(self, clear=True):
        """Remove selected user from database"""
        logger.debug('Remove user function')
        if clear:
            system('cls')
        print(
            f'-{static.readable_permission(self.permission)[0].upper()+static.readable_permission(self.permission)[1:]} User Removal Manager-')

        usr_del = input('Please enter username: ')
        if usr_del == '*':
            handle_user_abort()
            return False
        if not database.username_aviable(usr_del):
            # Username exists
            mail = database.get_mail(usr_del)
            permission = database.get_permissions(usr_del)
            perms = static.readable_permission(permission)
            print(
                f'\nAccount found:\n   Username: {usr_del}\n   Registered E-Mail Address: {mail}\n   Permission: {perms} ({permission})')
            inp = input(
                '\nDo you really wish to remove this account? (Y/N): ').lower()
            if inp == 'y':
                logger.debug('Account removal user-confirmed')
                if int(permission) > self.permission or self.permission == 0:
                    logger.debug('Permissions checked')
                    logger.info(
                        f'User {usr_del} has been unregistered by {self.username} (higher-perm-user-confirmed)')
                    database.remove_user(usr_del)
                    print(f'User {usr_del} (type: {perms}) was unregistered')
                    input('Press Enter to continue..')
                    return True
                else:
                    print(
                        f'Your permission level in insufficient to remove {perms} type account.')
                    logger.debug(
                        f'Insufficient permission level ({self.permission}) to remove {perms}({permission}) type account')
                    input('Press Enter to continue..')
                    return False
            else:
                handle_user_abort()
                return False
        else:
            logger.debug(f'Username {usr_del} is NOT linked with an account')
            print(f'There is no such account with username: {usr_del}')
            input('\nPress Enter to continue')
            self.remove_user(clear)

    # TODO: Improve function
    def create_user(self, clear=True, usr=None, mail=None):
        """Create new user with specified data"""
        logger.debug('Create user function')
        if clear:
            system('cls')
        print(
            f'-{static.readable_permission(self.permission)[0].upper()+static.readable_permission(self.permission)[1:]} Register Manager-')

        if not usr:
            usr = input('Enter username: ')

            if usr == '*':
                handle_user_abort()
                return False
        else:
            print(f'Username: {usr}')

        if database.username_aviable(usr):
            if not mail:
                mail = input('Enter your email address: ').lower()
                # If mail is * go back
                if mail == '*':
                    handle_user_abort()
                    return False
            else:
                print(f'E-Mail Address: {mail}')
            # Check if the email address format is correct
            if static.check_mail(mail):
                logger.trace(f'Email format {mail} correct')
                pword = get_pword('Enter password: ')
                pword_rep = get_pword('Re-Enter password: ')
                # Check if passwords match
                if pword == pword_rep:
                    logger.debug('password match confirmed')
                    # Check if password meets the requirements
                    if static.check_password_requirements(pword):
                        logger.debug('password requirements confirmed')
                        permission_lev = input('Enter permission level: ')
                        if static.is_number(permission_lev):
                            perm_level = int(permission_lev)
                            if self.permission <= perm_level or self.permission == 0:
                                # All conditions met, register user
                                database.register_user(
                                    mail, usr, static.encrypt(pword), perm_level)
                                logger.info(
                                    f'Registered new user, name: {usr}')
                                print('\nRegistered successfully')
                                input('Press Enter to continue...')
                                if clear:
                                    system('cls')
                                return True
                            else:
                                print(
                                    f'Your permission level is not sufficient to create account with permission {perm_level}')
                                input('\nPress Enter to continue..')
                                if clear:
                                    system('cls')
                                self.create_user(
                                    clear=clear, usr=usr, mail=mail)
                        else:
                            print(
                                'Invalid permission level (permission level must be a number)')
                            print('-> 0: developer')
                            print('-> 1: administrator')
                            print('-> 2: admin')
                            print('-> 3: user')
                            input('\nPress Enter to continue..')
                            if clear:
                                system('cls')
                            self.create_user(clear=clear, usr=usr, mail=mail)
                    else:
                        # In case password does not meet requirements
                        invalid_password_requirements(clear=clear)
                        self.create_user(clear=clear, usr=usr, mail=mail)
                else:
                    # In case passwords does not match
                    logger.debug('passwords does not match')
                    print('\nPasswords does not match')
                    input('Press Enter to continue..')
                    if clear:
                        system('cls')
                    self.create_user(clear=clear, usr=usr, mail=mail)
            else:
                logger.debug(f'Email format {mail} incorrect')
                print('\nEmail format is invalid (___@___.___)')
                input('Press Enter to continue..')
                if clear:
                    system('cls')
                self.create_user(clear=clear, usr=usr)
        else:
            logger.debug('Username is taken')
            print('\nThis username is not aviable, do you want to override this setting?')
            cnfrm = input('Y/N: ')
            if cnfrm.lower() == 'y':
                logger.debug('Username override confirmed')
                perms = database.get_permissions(usr)
                if perms > self.permission:
                    logger.debug(
                        'Override successfull, permission level is sufficient')
                    database.remove_user(usr)
                    logger.info(
                        'Unregistering {}, his perm level was: {}; user removed by: {}, with perm level: {}', usr, perms, usr, self.permission)
                    print(
                        f'User {usr} was unregistered, his perm level was: {perms}')
                    input('\nPress Enter to continue..')
                    self.create_user(clear=clear, usr=usr)
                else:
                    logger.debug(
                        'Override function failed, permission level is not sufficient')
                    perms = static.readable_permission(
                        database.get_permissions(usr))
                    print(
                        f'Sorry, your permission level is not sufficient do delete {perms} type account')
                    input('\nPress Enter to continue..')
                    if clear:
                        system('cls')
                    return False
            else:
                handle_user_abort()
                if clear:
                    system('cls')
                return False

    # TODO: Add close account option
    def close_account(self):
        pass

    # TODO:Add functionality to change mail
    def change_mail(self, clear=True):
        print('This function is not available')
        input('\nPress Enter to continue..')
        if clear:
            system('cls')
        return False

    # TODO: Add functionality to edit user
    def edit_user(perm, clear=True):
        print('This function is not available')
        input('\nPress Enter to continue..')
        if clear:
            system('cls')
        return False
