import sys
import os
import hashlib
import sqlite3
import logging
from pathlib import Path
import re
import pword_mod

# Path to user database
DATABASE = 'database.db'
LOG_FILE = 'logs/logfile.log'


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.mkdir(directory)

    if not Path(file_path).is_file():
        with open(LOG_FILE, 'w'):
            pass

ensure_dir(LOG_FILE)

logger = logging.getLogger(__name__)

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s')


class GetOutOfLoop(Exception):
    pass

def is_number(num):
    try:
        _ = int(num)
        return True
    except GetOutOfLoop:
        return False


def create_database_tables():
    """Check if database exists, if not, create one"""
    logger.debug('Checking if database tables exists')
    if not Path(DATABASE).is_file():
        logger.warning('Database does not exists, creating new database')
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("""CREATE TABLE users (
                email TEXT,
                username TEXT,
                password TEXT,
                permlevel INTEGER
            )""")
        conn.commit()
        conn.close()
        return None
    else:
        logger.debug('Database exists.')
        return None


def get_database_tables():
    """Will return all saved info"""
    logger.debug('Accessing all database tables')
    create_database_tables()
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    data = c.fetchall()
    conn.commit()
    conn.close()
    logger.debug('Database tables returned, data: %s', data)
    return data


def delete_database_table():
    logger.info('removing whole database table')
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM users")
    conn.commit()
    conn.close()
    logger.debug('Whole database was deleted')


def unregister(usr):
    logger.info('removing user %s from database', usr)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username=:usr_name", {'usr_name': usr})
    conn.commit()
    conn.close()
    logger.debug('user unregistered')


def get_database_data(usr):
    create_database_tables()
    logger.debug('finding user %s details to change permission level', usr)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=:usr_name", {'usr_name': usr})
    fetch = c.fetchone()
    conn.commit()
    conn.close()
    return fetch


def file_register(mail, usr, pw, perms):
    """Register new user into database file"""
    logger.debug('adding user to database - mail: %s ; usr: %s ; enc_pwd: %s ; perms: %s', mail, usr, pw, perms)
    try:
        create_database_tables()
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES(:email, :username, :password, :permlevel)", {'email': mail, 'username': usr, 'password': pw, 'permlevel': perms})
        conn.commit()
        conn.close()
        logger.debug('user added successfully')
        return True
    except Exception as e:
        logger.error('unable to register user %s -> %s', usr, e)
        return False


def change_perm_level(usr, perm):
    """Change permission level of specified user"""
    logger.debug('changing permission level of user %s, to %s', usr, perm)
    # Get database data, to be able to register new user under same data (with changed permission level)
    fetch = get_database_data(usr)
    # extract database data to multiple vars
    curpermlvl = fetch[3]
    mail = fetch[0]
    pw = fetch[2]

    if int(curpermlvl) > int(perm):
        logger.debug('found user info: (usr: %s, mail: %s, enc-pw: %s, perms: %s) --> ELEVATION to %s', usr, mail, pw, curpermlvl, perm)
    elif int(curpermlvl) < int(perm):
        logger.debug('found user info: (usr: %s, mail: %s, enc-pw: %s, perms: %s) --> DEMOTION to %s', usr, mail, pw, curpermlvl, perm)
    else:
        logger.debug('found user info: (usr: %s, mail: %s, enc-pw: %s, perms: %s) --> PERMS EQUAL')
        return None
    # unregister extracted user
    unregister(usr)
    # register extracted user back, with diffirent permission
    file_register(mail, usr, pw, perm)
    logger.debug('permission level changed successfully')


def logged_in(usr):
    """User-side for Logged-In"""
    def get_pass(usr):
        """Get encrypted password from username in database"""
        logger.debug('finding password for %s', usr)
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=:usr_name", {'usr_name': usr})
        fetch = c.fetchone()
        conn.commit()
        conn.close()
        logger.debug('password found: %s', fetch[2])
        return fetch[2]

    def get_mail(usr):
        """Get email address from username in database"""
        logger.debug('finding email for %s', usr)
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=:usr_name", {'usr_name': usr})
        fetch = c.fetchone()
        conn.commit()
        conn.close()
        logger.debug('email address found: %s', fetch[0])
        return fetch[0]

    def get_perm_level(usr):
        """Get encrypted password from username in database"""
        logger.debug('finding permission level for %s', usr)
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=:usr_name", {'usr_name': usr})
        fetch = c.fetchone()
        conn.commit()
        conn.close()
        permlvl = fetch[3]
        logger.debug('permission level found: %s', permlvl)
        return permlvl

    def perm_lvl_readable(permlvl):
        val = 'unknown'
        if permlvl == 3:
            val = 'user'
        elif permlvl == 2:
            val = 'admin'
        elif permlvl == 1:
            val = 'superadmin'
        elif permlvl == 0:
            val = 'developer'
        logger.debug('level interpreted as: %s', val)
        return val

    def maxlevel():
        logger.debug('Showing maxlevel options')
        print(f' ->1: Create new user')
        print(f' ->2: Remove existing user')
        print(f' ->3: Edit existing user')
        print(f' ->4: Change your E-Mail address')
        print(f' ->5: Change your password')
        print(f' ->6: Python DeveloperShell')
        print(f' ->7: Log-out')

    def superadmin():
        logger.debug('Showing superadmin options')
        print(f' ->1: Create new user')
        print(f' ->2: Remove existing user')
        print(f' ->3: Edit existing user')
        print(f' ->4: Change your E-Mail address')
        print(f' ->5: Change your password')
        print(f' ->6: Log-out')

    def admin():
        logger.debug('Showing admin options')
        print(f' ->1: Create new user')
        print(f' ->2: Remove existing user')
        print(f' ->3: Edit existing user')
        print(f' ->4: Change your E-Mail address')
        print(f' ->5: Change your password')
        print(f' ->6: Log-out')

    def user():
        logger.debug('Showing user options')
        print(f' ->1: Change E-Mail address')
        print(f' ->2: Change password')
        print(f' ->3: Log-out')

    def change_pwd(override=False):
        """Change password of logged user"""
        logger.debug('trying to change password of %s', usr)
        os.system('cls')
        print('-Change password-')

        def check_pword(pw):
            """Check base requirements for password"""
            logger.debug('checking password requirements')
            rules = [
                lambda s: any(x.isupper() for x in s),  # must have at least one uppercase
                lambda s: any(x.islower() for x in s),  # must have at least one lowercase
                lambda s: any(x.isdigit() for x in s),  # must have at least one digit
                lambda s: len(s) >= 7                   # must be at least 7 characters
            ]
            if all(rule(pw) for rule in rules):
                # All rules passed
                logger.debug('pass requirements met')
                return True
            else:
                # Rule/s not passed
                logger.debug('pass requirements not met')
                return False

        if not override:
            inp = input(f'Hello {usr}, do you want to change your password? (Y/N): ').lower()
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
            if hashlib.sha224(old_pass.encode('UTF-8')).hexdigest() == get_pass(usr) or override:
                logger.debug('Old password is correct (or override is ON)')
                new_pass = pword_mod.get_pword('Enter new password: ')
                new_pass2 = pword_mod.get_pword('Re-Enter new password: ')
                if new_pass == new_pass2:
                    logger.debug('New passwords are matching')
                    if check_pword(new_pass):
                        logger.debug('Password requirements are met')
                        mail = get_mail(usr)
                        perm_level = get_perm_level(usr)
                        unregister(usr)
                        logger.info('User %s Unregistered (to change password)', usr)
                        enc_pass = hashlib.sha224(new_pass.encode('UTF-8')).hexdigest()
                        file_register(mail, usr, enc_pass, perm_level)
                        logger.info('User %s was registered with new password')
                        logger.debug('New encrypted password of %s is: %s', usr, enc_pass)
                        print('\nPassword has been changed successfully')
                        input('Press Enter to continue..')
                        main_log()
                    else:
                        logger.debug('password requirements not met')
                        print('\nPassword does not meet requirements. Must contain at least:')
                        print('  1 Uppercase letter \n  1 Lowercase letter \n  1 Number \n  Minimum length of 7 characters')
                        input('Press Enter to continue..')
                        change_pwd(True)
                        logger.debug('Restarting with override (yes prompt and old pass entry)')

                else:
                    logger.debug('Passwords are not matching')
                    print('\nPasswords are not matching')
                    input('Press any key to continue..')
                    logger.debug('Restarting with override (yes prompt and old pass entry)')
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

    # TODO: function
    def change_mail():
        """Change email of logged user"""
        print('This function is not available')
        input('\nPress Enter to continue..')
        os.system('cls')
        main_log()

    # TODO: function
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
        print(f'-{perm_lvl_readable(perm)[0].upper()+perm_lvl_readable(perm)[1:]} User Management-')

        def check_usr(usr):
            """Check if username exists in database"""
            logger.debug('checking username availability')
            create_database_tables()
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=:usr_name", {'usr_name': usr})
            fetch = c.fetchone()
            conn.commit()
            conn.close()
            if type(fetch) == tuple:
                # User found, return False
                logger.debug('username taken')
                return False
            else:
                # No such user, return True
                return True
            logger.debug('username available')

        usr_del = input('Please enter username: ')
        if usr_del == '*':
            logger.debug('user-removal aborted')
            main_log()
        if not check_usr(usr_del):
            # Username exists
            logger.debug('Username %s is linked with an account', usr_del)
            mail = get_mail(usr_del)
            permission = get_perm_level(usr_del)
            perms = perm_lvl_readable(permission)
            print(f'\nAccount found:\n   Username: {usr_del}\n   Registered E-Mail Address: {mail}\n   Permission: {perms} ({permission})')
            inp = input('\nDo you really wish to remove this account? (Y/N): ').lower()
            if inp == 'y':
                logger.debug('Account removal user-confirmed')
                if int(permission) > perm or perm == 0:
                    logger.debug('Permissions checked')
                    logger.info('User %s has been unregistered by %s (higher-perm-user-confirmed)', usr_del, usr)
                    unregister(usr_del)
                    print(f'User {usr_del} (type: {perms}) was unregistered')
                    input('Press Enter to continue..')
                    main_log()
                else:
                    print('Your permission level in insufficient to remove {perms} type account.')
                    input('Press Enter to continue..')
                    main_log()
            else:
                input('Aborting, Press Enter to continue..')
                main_log()
        else:
            logger.debug('Username %s is NOT linked with an account', usr_del)
            print(f'There is no such account with username: {usr_del}')
            input('\nPress Enter to continue')
            remove_user(perm)

    # TODO: Add Logger
    def create_user(perm, usr=None, mail=None):
        """Create new user with specified data"""
        logger.debug('Create user function')
        os.system('cls')
        print(f'-{perm_lvl_readable(perm)[0].upper()+perm_lvl_readable(perm)[1:]} Register-')

        def check_usr(usr):
            """Check if username exists in database"""
            logger.debug('checking username availability')
            create_database_tables()
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=:usr_name", {'usr_name': usr})
            fetch = c.fetchone()
            conn.commit()
            conn.close()
            if type(fetch) == tuple:
                # User found, return False
                logger.debug('username taken')
                return False
            else:
                # No such user, return True
                return True
            logger.debug('username available')

        def check_pword(pw):
            """Check base requirements for password"""
            logger.debug('checking password requirements')
            rules = [
                lambda s: any(x.isupper() for x in s),  # must have at least one uppercase
                lambda s: any(x.islower() for x in s),  # must have at least one lowercase
                lambda s: any(x.isdigit() for x in s),  # must have at least one digit
                lambda s: len(s) >= 7                   # must be at least 7 characters
            ]
            if all(rule(pw) for rule in rules):
                # All rules passed
                logger.debug('pass requirements met')
                return True
            else:
                # Rule/s not passed
                logger.debug('pass requirements not met')
                return False

        def check_mail(mail):
            """Check if email format is correct"""
            logger.debug('checking email format')
            if re.match(r'[^@]+@[^@]+\.[^@]', mail):
                logger.debug('email format correct')
                return True
            else:
                logger.debug('email format incorrect')
                return False
            if not usr:
                usr = input('Enter username: ').lower()
            logger.debug('trying to create account, username: {}'.format(usr))
            if usr == '*':
                logger.debug('leaving function (*)')
                os.system('cls')
                main_log()

        if not usr:
            usr = input('Enter username: ')
        else:
            print(f'Username: {usr}')

        if usr == '*':
            main_log()

        # TODO: complete function
        if check_usr(usr) is True:
            if not mail:
                mail = input('Enter your email address: ').lower()
                # If mail is * go back
                if mail == '*':
                    logger.info('registration aborted')
                    main_log()
            else:
                print(f'E-Mail Address: {mail}')
            # Check if the email address format is correct
            mail_valid = check_mail(mail)
            if mail_valid:
                pword = pword_mod.get_pword('Enter password: ')
                pword_rep = pword_mod.get_pword('Re-Enter password: ')
                # Check if passwords match
                if pword == pword_rep:
                    logger.debug('password match confirmed')
                    # Check if password meets the requirements
                    if check_pword(pword):
                        logger.debug('password requirements confirmed')
                        permission_lev = input('Enter permission level: ')
                        if is_number(permission_lev):
                            perm_level = int(permission_lev)
                            if perm < perm_level or perm == 0:
                                # All conditions met, register user
                                if file_register(mail, usr, hashlib.sha224(pword.encode('UTF-8')).hexdigest(), perm_level):
                                    logger.info('Registered new user, name: {}'.format(usr))
                                    print('\nRegistered successfully')
                                    input('Press Enter to continue...')
                                    os.system('cls')
                                    main_log()
                                else:
                                    # In case of failure in file_register()
                                    logger.error('Register encryption function failed')
                                    print('\nRegister failed, please see log details (%s)', LOG_FILE)
                                    print('In case you are unable to figure out how to fix this issue, please send logfile to the developer')
                                    input('Press Enter to continue...')
                                    os.system('cls')
                                    main_log()
                            else:
                                print(f'Your permission level is not sufficient to create account with permission {perm_level}')
                                input('\nPress Enter to continue..')
                                os.system('cls')
                                create_user(perm, usr, mail)
                        else:
                            print('Invalid permission level (permission level must be a number)')
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
                        print('\nPassword does not meet requirements. Must contain at least:')
                        print('  1 Uppercase letter \n  1 Lowercase letter \n  1 Number \n  Minimum length of 7 characters')
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
                perms = get_perm_level(usr)
                if perms > perm:
                    logger.debug('Override successfull, permission level is sufficient')
                    unregister(usr)
                    logger.info('Unregistering %s, his perm level was: %s; user removed by: %s, with perm level: %s', usr, perms, usr, perm)
                    print(f'User {usr} was unregistered, his perm level was: {perms}')
                    input('\nPress Enter to continue..')
                    create_user(perm, usr)
                else:
                    logger.debug('Override function failed, permission level is not sufficient')
                    perms = perm_lvl_readable(get_perm_level(usr))
                    print(f'Sorry, your permission level is not sufficient do delete {perms} type account')
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
        logger.debug('action choosed: %s, perm level: %s', action, n)
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
                    logger.debug('Choosed %s with perm %s', act, n)
                    main()
                elif act == 6:
                    logger.debug('Choosed %s with perm %s', act, n)
                    try:
                        while True:
                            os.system('cls')
                            print('-Python shell-')
                            print('Developer access (enter direct python commands)\n')
                            print(f'Python {sys.version}')
                            print('Type "help" for more information')
                            while True:
                                inp = input('>>>')
                                if inp.lower() != 'exit' and inp.lower() != 'help':
                                    logger.info('Python DeveloperShell: %s', inp)
                                    try:
                                        exec(inp)
                                    except Exception as e:
                                        print('  Exception handeler -> Error:')
                                        print(f'    Error: {e}')
                                        logger.warning('Python DeveloperShell returned Error -> %s', e)
                                elif inp.lower() == 'help':
                                    logger.debug('Python DeveloperShell help')
                                    os.system('cls')
                                    print('-Help-\n')
                                    print('This is a python developer shell')
                                    print('You can execute direct python commands into program')
                                    print('Warning: executing wrong commands can break this instance of the program')
                                    print('If you don\'t know what are you doing, please exit the developer shell')
                                    print('-------------------------------------------------------------------------')
                                    print('Type \'exit\' to exit developer shell')
                                    inp = input('\nPress enter to return to developer shell\n')
                                    if inp.lower() == 'exit':
                                        logger.debug('Python DeveloperShell exit (in help)')
                                        main_log()
                                    else:
                                        break
                                else:
                                    logger.debug('Python DeveloperShell exit')
                                    raise GetOutOfLoop
                            else:
                                continue
                    except GetOutOfLoop:
                        main_log()
                elif act == 5:
                    logger.debug('Choosed %s with perm %s', act, n)
                    change_pwd()
                elif act == 4:
                    logger.debug('Choosed %s with perm %s', act, n)
                    change_mail()
                elif act == 3:
                    logger.debug('Choosed %s with perm %s', act, n)
                    edit_user(n)
                elif act == 2:
                    logger.debug('Choosed %s with perm %s', act, n)
                    remove_user(n)
                elif act == 1:
                    logger.debug('Choosed %s with perm %s', act, n)
                    create_user(n)
                else:
                    logger.debug('Choosed %s with perm %s (no such option)', act, n)
                    print('Error, no such option option')
                    input('\nPress Enter to continue..')
                    os.system('cls')
                    main_log()
            else:
                # Error, wrong permission level
                logger.error('Error: Permission level not recognized')
                print('Error -> Your account has bad permission level, please contact admin or create new account.')
                print('Temporarily, you will be asigned permission level 3 - (user)')
                input('\nPress Enter to continue..')
                main_log(3)
        except ValueError:
            if action == '*':
                main()
            else:
                logger.error('Choosed %s with perm %s (no such option - not a number)', action, n)
                print('Error, no such option option (must be number)')
                input('\nPress Enter to continue..')
                os.system('cls')
                main_log()

    def main_log(perms=None):
        logger.debug('Logged as %s', usr)
        os.system('cls')
        print(f'-Welcome {usr}-\n')
        pw = get_pass(usr)
        mail = get_mail(usr)
        if perms:
            permlvl = perms
            perm = perm_lvl_readable(permlvl)
        else:
            permlvl = get_perm_level(usr)
            perm = perm_lvl_readable(permlvl)

        print(f'(Your current E-Mail: {mail})')
        if perms:
            print(f'(Your permission level: Temporal {perm} - Contact developer for more info or create new account.)')
        else:
            print(f'(Your permission level: {perm})')
        print(f'(Your Encrypted password: {pw})\n')

        # * Permission level
        if permlvl == 0:
            maxlevel()
        # SuperAdmin permission level
        elif permlvl == 1:
            superadmin()
        # Admin permission level
        elif permlvl == 2:
            admin()
        # User permission level
        elif permlvl == 3:
            user()
        get_inputs(permlvl)

    main_log()


def register():
    """Main register function"""
    def check_usr(usr):
        """Check if username exists in database"""
        logger.debug('checking username availability')
        create_database_tables()
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=:usr_name", {'usr_name': usr})
        fetch = c.fetchone()
        conn.commit()
        conn.close()
        if type(fetch) == tuple:
            # User found, return False
            logger.debug('username taken')
            return False
        else:
            # No such user, return True
            logger.debug('username available')
            return True

    def check_pword(pw):
        """Check base requirements for password"""
        logger.debug('checking password requirements')
        rules = [
            lambda s: any(x.isupper() for x in s),  # must have at least one uppercase
            lambda s: any(x.islower() for x in s),  # must have at least one lowercase
            lambda s: any(x.isdigit() for x in s),  # must have at least one digit
            lambda s: len(s) >= 7                   # must be at least 7 characters
        ]
        if all(rule(pw) for rule in rules):
            # All rules passed
            logger.debug('pass requirements met')
            return True
        else:
            # Rule/s not passed
            logger.debug('pass requirements not met')
            return False

    def check_mail(mail):
        """Check if email format is correct"""
        logger.debug('checking email format')
        if re.match(r'[^@]+@[^@]+\.[^@]', mail):
            logger.debug('email format correct')
            return True
        else:
            logger.debug('email format incorrect')
            return False

    def reg():
        """User-side for register"""
        logger.debug('registration process started')
        print('-Register-')
        mail = input('Enter your email address: ').lower()
        # If mail is * go back
        if mail == '*':
            logger.info('registration aborted')
            main()
        else:
            # Check if the email address format is correct
            mail_valid = check_mail(mail)
            if mail_valid:
                usr_name = input('Enter your new username: ').lower()
                # Check if the username is available
                usr_valid = check_usr(usr_name)
                if usr_valid:
                    logger.debug('registration username valid')
                    pword = pword_mod.get_pword('Enter password: ')
                    pword_rep = pword_mod.get_pword('Re-Enter password: ')
                    # Check if passwords match
                    if pword == pword_rep:
                        logger.debug('password match confirmed')
                        # Check if password meets the requirements
                        if check_pword(pword):
                            logger.debug('password requirements confirmed')
                            # All conditions met, register user
                            if file_register(mail, usr_name, hashlib.sha224(pword.encode('UTF-8')).hexdigest(), 3):
                                logger.info('Registered new user, name: {}'.format(usr_name))
                                print('\nRegistered successfully')
                                input('Press Enter to continue...')
                                os.system('cls')
                                main()
                            else:
                                # In case of failure in file_register()
                                logger.error('Register encryption function failed')
                                print('\nRegister failed, please see log details (%s)', LOG_FILE)
                                print('In case you are unable to figure out how to fix this issue, please send logfile to the developer')
                                input('Press Enter to continue...')
                                os.system('cls')
                                main()
                        else:
                            # In case password does not meet requirements
                            logger.debug('password requirements not met')
                            print('\nPassword does not meet requirements. Must contain at least:')
                            print('  1 Uppercase letter \n  1 Lowercase letter \n  1 Number \n  Minimum length of 7 characters')
                            input('Press Enter to continue..')
                            os.system('cls')
                            reg()
                    else:
                        # In case passwords does not match
                        logger.debug('passwords does not match')
                        print('\nPasswords does not match')
                        input('Press Enter to continue..')
                        os.system('cls')
                        reg()

                else:
                    # Username is aleardy taken
                    logger.debug('registration username invalid (taken)')
                    print('\nThis username is not available')
                    input('Press Enter to continue..')
                    os.system('cls')
                    reg()
            else:
                logger.debug('registration email format invalid')
                print('\nEmail format is invalid (___@___.___)')
                input('Press Enter to continue..')
                os.system('cls')
                reg()
    reg()


def login():
    """Main login function"""
    def verify(usr, pw):
        """Check if user with entered name and pass exists in database"""
        logger.debug('verifying username and password for logging-in')
        create_database_tables()
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=:usr_name AND password=:pword", {'usr_name': usr, 'pword': pw})
        fetch = c.fetchone()
        conn.commit()
        conn.close()
        if type(fetch) == tuple:
            # User with entered specs found, return True
            logger.debug('user verification confirmed (name: %s)', usr)
            return True
        else:
            # User with entered specs not found, return False
            logger.debug('user verification failed (name: %s)', usr)
            return False

    def log():
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
        if verify(usr_name, pword_enc):
            # User exists
            logger.debug('user information confirmed, user exists')
            logger.info('user %s logged.', usr_name)
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
            log()
    log()


def default_user(enabled=True, pword='admin'):
    if enabled:
        if get_database_data('admin') is None:
            file_register('None set', 'admin', hashlib.sha224(pword.encode('UTF-8')).hexdigest(), 1)



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
        logger.info('choice: END (*)')
        logger.info('Program ended by user')
        input('Press enter to end program..')
        exit()
    elif register_prompt.lower() == '*':
        print(get_database_tables())
        input('Press Enter to continue..')
        os.system('cls')
        main()
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
        default_user()
        main()
    except Exception as e:
        logger.exception('-Main exception-')
        logger.critical('Program Failed: %s', e)
        print('\nProgram failed, send this error message to developer:')
        print(f' ->  Error: {e}')
        input('Press Enter to restart..')
        os.system('cls')
        main()
else:
    logger.info('Program started non-directly')
