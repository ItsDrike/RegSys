import hashlib
import os
import sys
from loguru import logger
import main.static as static
import main.database as database
import main.interface as interface

import pword_mod

# Path to user database
DATABASE = 'database.db'
LOG_FILE = 'logs/logfile.log'

see_logs = True


static.ensure_dir(LOG_FILE)

logger.add(LOG_FILE, level='DEBUG', format='<green>{time: YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level>  | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>',
           filter=None, colorize=None, serialize=False, backtrace=True, diagnose=True, enqueue=False, catch=True)

if not see_logs:
    logger.remove(0)


def logged_in(usr):
    """User-side for Logged-In"""
    # TODO: Add close account option

    def change_pwd(override=False):
        """Change password of logged user"""
        logger.debug('trying to change password of {}', usr)
        os.system('cls')
        print('-Change password-')

        if not override:
            inp = input(
                f'Hello {usr}, do you want to change your password? (Y/N): ').lower()
        else:
            logger.debug('Overriding confirmation prompt')
            inp = 'y'
        if inp == 'y':
            logger.debug('Confirmation successful')
            if not override:
                old_pass = pword_mod.get_pword('Enter your password: ')
            else:
                logger.debug('Overriding old_pass entry')
                print('')
                old_pass = ''
            if hashlib.sha224(old_pass.encode('UTF-8')).hexdigest() == database.get_pass(usr) or override:
                logger.debug('Old password is correct (or override is ON)')
                new_pass = pword_mod.get_pword('Enter new password: ')
                new_pass2 = pword_mod.get_pword('Re-Enter new password: ')
                if new_pass == new_pass2:
                    logger.debug('New passwords are matching')
                    if static.check_password_requirements(new_pass):
                        logger.debug('Password requirements are met')
                        mail = database.get_mail(usr)
                        perm_level = database.get_permissions(usr)
                        database.remove_user(usr)
                        logger.info(
                            'User {} Unregistered (to change password)', usr)
                        enc_pass = hashlib.sha224(
                            new_pass.encode('UTF-8')).hexdigest()
                        database.register_user(mail, usr, enc_pass, perm_level)
                        logger.info('User {} was registered with new password')
                        logger.debug(
                            'New encrypted password of {} is: {}', usr, enc_pass)
                        print('\nPassword has been changed successfully')
                        input('Press Enter to continue..')
                        main_log()
                    else:
                        logger.debug('password requirements not met')
                        print(
                            '\nPassword does not meet requirements. Must contain at least:')
                        print(
                            '  1 Uppercase letter \n  1 Lowercase letter \n  1 Number \n  Minimum length of 7 characters')
                        input('Press Enter to continue..')
                        change_pwd(True)
                        logger.debug(
                            'Restarting with override (yes prompt and old pass entry)')

                else:
                    logger.debug('Passwords are not matching')
                    print('\nPasswords are not matching')
                    input('Press any key to continue..')
                    logger.debug(
                        'Restarting with override (yes prompt and old pass entry)')
                    change_pwd(True)
            else:
                logger.debug('Old password incorrect')
                print('\nYour password is incorrect (first, enter your old password)')
                input('Press Enter to continue..')
                change_pwd()

        else:
            logger.debug('User-Aborted')
            input('Password change aborted, Press Enter to continue..')
            main_log()

    # TODO:Add functionality to change mail
    def change_mail():
        """Change email of logged user"""
        print('This function is not available')
        input('\nPress Enter to continue..')
        os.system('cls')
        main_log()

    # TODO: Add functionality to edit user
    def edit_user(perm):
        """Edit database information about selected user"""
        print('This function is not available')
        input('\nPress Enter to continue..')
        os.system('cls')
        main_log()

    def remove_user(perm):
        """Remove selected user from database"""
        logger.debug('Remove user function')
        os.system('cls')
        print(
            f'-{static.readable_permission(perm)[0].upper()+static.readable_permission(perm)[1:]} User Management-')

        usr_del = input('Please enter username: ')
        if usr_del == '*':
            logger.debug('user-removal aborted')
            main_log()
        if not database.username_aviable(usr_del):
            # Username exists
            logger.debug('Username {} is linked with an account', usr_del)
            mail = database.get_mail(usr_del)
            permission = database.get_permissions(usr_del)
            perms = static.readable_permission(permission)
            print(
                f'\nAccount found:\n   Username: {usr_del}\n   Registered E-Mail Address: {mail}\n   Permission: {perms} ({permission})')
            inp = input(
                '\nDo you really wish to remove this account? (Y/N): ').lower()
            if inp == 'y':
                logger.debug('Account removal user-confirmed')
                if int(permission) > perm or perm == 0:
                    logger.debug('Permissions checked')
                    logger.info(
                        'User {} has been unregistered by {} (higher-perm-user-confirmed)', usr_del, usr)
                    database.remove_user(usr_del)
                    print(f'User {usr_del} (type: {perms}) was unregistered')
                    input('Press Enter to continue..')
                    main_log()
                else:
                    print(
                        'Your permission level in insufficient to remove {perms} type account.')
                    logger.debug(
                        'Insufficient permission level ({}) to remove {}({}) type account', perm, perms, permission)
                    input('Press Enter to continue..')
                    main_log()
            else:
                input('Aborting, Press Enter to continue..')
                main_log()
        else:
            logger.debug('Username {} is NOT linked with an account', usr_del)
            print(f'There is no such account with username: {usr_del}')
            input('\nPress Enter to continue')
            remove_user(perm)

    def create_user(perm, usr=None, mail=None):
        """Create new user with specified data"""
        logger.debug('Create user function')
        os.system('cls')
        print(
            f'-{static.readable_permission(perm)[0].upper()+static.readable_permission(perm)[1:]} Register-')

        if not usr:
            usr = input('Enter username: ')
        else:
            print(f'Username: {usr}')

        if usr == '*':
            main_log()

        if database.username_aviable(usr) is True:
            if not mail:
                mail = input('Enter your email address: ').lower()
                # If mail is * go back
                if mail == '*':
                    logger.info('registration aborted')
                    main_log()
            else:
                print(f'E-Mail Address: {mail}')
            # Check if the email address format is correct
            if static.check_mail(mail):
                pword = pword_mod.get_pword('Enter password: ')
                pword_rep = pword_mod.get_pword('Re-Enter password: ')
                # Check if passwords match
                if pword == pword_rep:
                    logger.debug('password match confirmed')
                    # Check if password meets the requirements
                    if static.check_password_requirements(pword):
                        logger.debug('password requirements confirmed')
                        permission_lev = input('Enter permission level: ')
                        if static.is_number(permission_lev):
                            perm_level = int(permission_lev)
                            if perm <= perm_level or perm == 0:
                                # All conditions met, register user
                                if database.register_user(mail, usr, hashlib.sha224(pword.encode('UTF-8')).hexdigest(), perm_level):
                                    logger.info(
                                        'Registered new user, name: {}'.format(usr))
                                    print('\nRegistered successfully')
                                    input('Press Enter to continue...')
                                    os.system('cls')
                                    main_log()
                                else:
                                    # In case of failure in database.register_user()
                                    logger.error(
                                        'Register encryption function failed')
                                    print(
                                        '\nRegister failed, please see log details ({})', LOG_FILE)
                                    print(
                                        'In case you are unable to figure out how to fix this issue, please send logfile to the developer')
                                    input('Press Enter to continue...')
                                    os.system('cls')
                                    main_log()
                            else:
                                print(
                                    f'Your permission level is not sufficient to create account with permission {perm_level}')
                                input('\nPress Enter to continue..')
                                os.system('cls')
                                create_user(perm, usr, mail)
                        else:
                            print(
                                'Invalid permission level (permission level must be a number)')
                            print('-> 0: developer')
                            print('-> 1: administrator')
                            print('-> 2: admin')
                            print('-> 3: user')
                            input('\nPress Enter to continue..')
                            os.system('cls')
                            create_user(perm, usr, mail)
                    else:
                        # In case password does not meet requirements
                        logger.debug('password requirements not met')
                        print(
                            '\nPassword does not meet requirements. Must contain at least:')
                        print(
                            '  1 Uppercase letter \n  1 Lowercase letter \n  1 Number \n  Minimum length of 7 characters')
                        input('Press Enter to continue..')
                        os.system('cls')
                        create_user(perm, usr, mail)
                else:
                    # In case passwords does not match
                    logger.debug('passwords does not match')
                    print('\nPasswords does not match')
                    input('Press Enter to continue..')
                    os.system('cls')
                    create_user(perm, usr, mail)
            else:
                logger.debug('registration email format invalid')
                print('\nEmail format is invalid (___@___.___)')
                input('Press Enter to continue..')
                os.system('cls')
                create_user(perm, usr)

            print('This function is not aviable')
            logger.debug('Username checks complete, creating account')
            logger.error('WIP: this function is not yet completed.')
        else:
            logger.debug('Username is taken')
            print('\nThis username is not aviable, do you want to override this setting?')
            cnfrm = input('Y/N: ')
            if cnfrm.lower() == 'y':
                logger.debug('Username override confirmed')
                perms = database.get_permissions(usr)
                if perms > perm:
                    logger.debug(
                        'Override successfull, permission level is sufficient')
                    database.remove_user(usr)
                    logger.info(
                        'Unregistering {}, his perm level was: {}; user removed by: {}, with perm level: {}', usr, perms, usr, perm)
                    print(
                        f'User {usr} was unregistered, his perm level was: {perms}')
                    input('\nPress Enter to continue..')
                    create_user(perm, usr)
                else:
                    logger.debug(
                        'Override function failed, permission level is not sufficient')
                    perms = static.readable_permission(
                        database.get_permissions(usr))
                    print(
                        f'Sorry, your permission level is not sufficient do delete {perms} type account')
                    input('\nPress Enter to continue..')
                    os.system('cls')
                    create_user(perm)

            else:
                logger.debug('restarting, override function aborted')
                input('\nPress Enter to continue..')
                os.system('cls')
                create_user(perm)

        input('\nPress Enter to continue..')
        os.system('cls')
        main_log()

    def get_inputs(n):
        """Get input from user to choose option, based on user's permission level"""
        logger.debug('Choosing from options')
        action = input('\nEnter action number: ')
        logger.debug('action choosed: {}, perm level: {}', action, n)
        try:
            act = int(action)
            if n == 3:
                # User
                if act == 3:
                    main()
                elif act == 2:
                    change_pwd()
                elif act == 1:
                    change_mail()
                else:
                    print('Error, no such option option')
                    input('\nPress Enter to continue..')
                    os.system('cls')
                    main_log()
            elif n == 2:
                # Admin
                if act == 6:
                    main()
                elif act == 5:
                    change_pwd()
                elif act == 4:
                    change_mail()
                elif act == 3:
                    edit_user(n)
                elif act == 2:
                    remove_user(n)
                elif act == 1:
                    create_user(n)
                else:
                    print('Error, no such option option')
                    input('\nPress Enter to continue..')
                    os.system('cls')
                    main_log()
            elif n == 1:
                # SuperAdmin
                if act == 6:
                    main()
                elif act == 5:
                    change_pwd()
                elif act == 4:
                    change_mail()
                elif act == 3:
                    edit_user(n)
                elif act == 2:
                    remove_user(n)
                elif act == 1:
                    create_user(n)
                else:
                    print('Error, no such option option')
                    input('\nPress Enter to continue..')
                    os.system('cls')
                    main_log()
            elif n == 0:
                # Max Level
                if act == 7:
                    logger.debug('Choosed {} with perm {}', act, n)
                    main()
                elif act == 6:
                    logger.debug('Choosed {} with perm {}', act, n)
                    try:
                        while True:
                            os.system('cls')
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
                                    os.system('cls')
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
                                        main_log()
                                    else:
                                        break
                                else:
                                    logger.debug('Python DeveloperShell exit')
                                    raise static.GetOutOfLoop
                            else:
                                continue
                    except static.GetOutOfLoop:
                        main_log()
                elif act == 5:
                    logger.debug('Choosed {} with perm {}', act, n)
                    change_pwd()
                elif act == 4:
                    logger.debug('Choosed {} with perm {}', act, n)
                    change_mail()
                elif act == 3:
                    logger.debug('Choosed {} with perm {}', act, n)
                    edit_user(n)
                elif act == 2:
                    logger.debug('Choosed {} with perm {}', act, n)
                    remove_user(n)
                elif act == 1:
                    logger.debug('Choosed {} with perm {}', act, n)
                    create_user(n)
                else:
                    logger.debug(
                        'Choosed {} with perm {} (no such option)', act, n)
                    print('Error, no such option option')
                    input('\nPress Enter to continue..')
                    os.system('cls')
                    main_log()
            else:
                # Error, wrong permission level
                logger.error('Error: Permission level not recognized')
                print(
                    'Error -> Your account has bad permission level, please contact admin or create new account.')
                print('Temporarily, you will be assigned permission level 3 - (user)')
                input('\nPress Enter to continue..')
                main_log(3)
        except ValueError:
            if action == '*':
                main()
            else:
                logger.error(
                    'Choosed {} with perm {} (no such option - not a number)', action, n)
                print('Error, no such option option (must be number)')
                input('\nPress Enter to continue..')
                os.system('cls')
                main_log()

    def main_log(perms=None):
        logger.debug('Logged as {}', usr)
        os.system('cls')
        print(f'-Welcome {usr}-\n')
        pw = database.get_pass(usr)
        mail = database.get_mail(usr)
        if perms:
            permlvl = perms
            perm = static.readable_permission(permlvl)
        else:
            permlvl = database.get_permissions(usr)
            perm = static.readable_permission(permlvl)

        print(f'(Your current E-Mail: {mail})')
        if perms:
            print(
                f'(Your permission level: Temporal {perm} - Contact developer for more info or create new account.)')
        else:
            print(f'(Your permission level: {perm})')
        print(f'(Your Encrypted password: {pw})\n')

        interface.show_menu(permlvl)
        get_inputs(permlvl)

    main_log()


def register():
    """Main register function"""
    logger.debug('registration process started')
    print('-Register-')
    mail = input('Enter your email address: ').lower()
    # If mail is * go back
    if mail == '*':
        logger.info('registration aborted')
        main()
    else:
        # Check if the email address format is correct
        if static.check_mail(mail):
            usr_name = input('Enter your new username: ').lower()
            # Check if the username is available
            usr_valid = database.username_aviable(usr_name)
            if usr_valid:
                logger.debug('registration username valid')
                pword = pword_mod.get_pword('Enter password: ')
                pword_rep = pword_mod.get_pword('Re-Enter password: ')
                # Check if passwords match
                if pword == pword_rep:
                    logger.debug('password match confirmed')
                    # Check if password meets the requirements
                    if static.check_password_requirements(pword):
                        logger.debug('password requirements confirmed')
                        # All conditions met, register user
                        if database.register_user(mail, usr_name, hashlib.sha224(pword.encode('UTF-8')).hexdigest(), 3):
                            logger.info(
                                'Registered new user, name: {}'.format(usr_name))
                            print('\nRegistered successfully')
                            input('Press Enter to continue...')
                            os.system('cls')
                            main()
                        else:
                            # In case of failure in database.register_user()
                            logger.error(
                                'Register encryption function failed')
                            print(
                                '\nRegister failed, please see log details ({})', LOG_FILE)
                            print(
                                'In case you are unable to figure out how to fix this issue, please send logfile to the developer')
                            input('Press Enter to continue...')
                            os.system('cls')
                            main()
                    else:
                        # In case password does not meet requirements
                        logger.debug('password requirements not met')
                        print(
                            '\nPassword does not meet requirements. Must contain at least:')
                        print(
                            '  1 Uppercase letter \n  1 Lowercase letter \n  1 Number \n  Minimum length of 7 characters')
                        input('Press Enter to continue..')
                        os.system('cls')
                        register()
                else:
                    # In case passwords does not match
                    logger.debug('passwords does not match')
                    print('\nPasswords does not match')
                    input('Press Enter to continue..')
                    os.system('cls')
                    register()

            else:
                # Username is already taken
                logger.debug('registration username invalid (taken)')
                print('\nThis username is not available')
                input('Press Enter to continue..')
                os.system('cls')
                register()
        else:
            logger.debug('registration email format invalid')
            print('\nEmail format is invalid (___@___.___)')
            input('Press Enter to continue..')
            os.system('cls')
            register()


def login():
    """Main login function"""
    """User-side for login"""
    logger.debug('logging-in process started')
    print('-Login-')
    usr_name = input('Enter your username: ').lower()
    # If name is * go back
    if usr_name == '*':
        logger.info('logging-in aborted')
        main()
    pword = pword_mod.get_pword('State your password: ')
    pword_enc = hashlib.sha224(pword.encode('UTF-8')).hexdigest()
    # Send username with encrypted password for verify
    if database.account_exists(usr_name, pword_enc):
        # User exists
        logger.debug('user information confirmed, user exists')
        logger.info('user {} logged.', usr_name)
        print('\nLogged in successfully')
        input('Press Enter to continue..')
        os.system('cls')
        # Go to logged screen
        logged_in(usr_name)
        return None
    else:
        # No such user
        logger.debug('username or password incorrect')
        print('\nInvalid username or password')
        input('Press Enter to continue..')
        os.system('cls')
        login()


def default_user(enabled=True, pword='admin'):
    if enabled:
        if database.username_aviable('admin') is True:
            database.register_user('None set', 'admin', hashlib.sha224(
                pword.encode('UTF-8')).hexdigest(), 1)


@logger.catch
def main():
    """Main User-Side Interface-"""
    logger.debug('main interface')
    os.system('cls')
    print('Welcome to RegSys Software, created by Koumakpet <koumakpet@hexadynamic.com>')
    print(' ->Login:            1')
    print(' ->Register:         2')
    print(' ->Exit/Go back:     *')
    register_prompt = input('\nWhat do you want to do?: ')
    if register_prompt.lower() == '2':
        # Register
        logger.info('choice: register (2)')
        os.system('cls')
        register()
    elif register_prompt.lower() == '1':
        # Log In
        logger.info('choice: login (1)')
        os.system('cls')
        login()
    elif register_prompt.lower() == '*':
        logger.debug('choice: END (*)')
        logger.info('Program ended by user')
        input('Press enter to end program..')
        exit()
    else:
        # Wrong option
        logger.debug('choice: invalid ({})'.format(register_prompt))
        print('Invalid choice')
        input('Press Enter to continue..')
        os.system('cls')
        main()


if __name__ == '__main__':
    logger.info('Program started directly')
    try:
        default_user(False)
        main()
    except Exception as e:
        logger.exception('-Main exception-')
        logger.critical('Program Failed: {}', e)
        print('\nProgram failed, send this error message to developer:')
        print(f' ->  Error: {e}')
        input('Press Enter to restart..')
        os.system('cls')
        main()
else:
    logger.info('Program started non-directly')
