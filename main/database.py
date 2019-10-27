from pathlib import Path
from importlib import import_module
import sqlite3

logger = import_module('RegSys').logger
static = import_module('RegSys').static


def create(DATABASE='database.db'):
    '''Check for database existence

    Keyword Arguments:
        DATABASE {string} -- Path to database file (default: {'database.db'})

    Returns:
        boolean -- Database created
    '''
    logger.trace('Checking if database exists')
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
        return True
    else:
        logger.trace('Database exists, no action required.')
        return False


def get_all_users(DATABASE='database.db'):
    # TODO: Add documentation for return value type
    '''Returns all saved users

    Keyword Arguments:
        DATABASE {string} -- Path to database file (default: {'database.db'})

    Returns:
        [type] -- Database table dump
    '''
    logger.trace('Accessing all database tables')
    create()
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    data = c.fetchall()
    conn.commit()
    conn.close()
    logger.trace(f'Database tables returned, data: {data}')
    return data


def delete_all_users(DATABASE='database.db'):
    '''Removes all users in database

    Keyword Arguments:
        DATABASE {string} -- Path to database file (default: {'database.db'})
    '''
    logger.warning('Removing all users from database')
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM users")
    conn.commit()
    conn.close()
    logger.trace('Removed all users from database')


def remove_user(usr, DATABASE='database.db'):
    '''Removes specified user from database

    Arguments:
        usr {string} -- Username

    Keyword Arguments:
        DATABASE {string} -- Path to database file (default: {'database.db'})
    '''
    logger.debug('removing user {} from database', usr)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username=:usr_name", {'usr_name': usr})
    conn.commit()
    conn.close()
    logger.trace('user removed')


def register_user(mail, usr, pw, perms, DATABASE='database.db'):
    '''Register new user

    Arguments:
        mail {string} -- Users E-Mail address
        usr {string} -- Username
        pw {string} -- Encrypted password
        perms {string} -- Permission level

    Keyword Arguments:
        DATABASE {string} -- Path to database file (default: {'database.db'})

    Returns:
        boolean -- User registered
    '''
    logger.trace(
        'adding user to database - mail: {} ; usr: {} ; enc_pwd: {} ; perms: {}', mail, usr, pw, perms)
    try:
        create()
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES(:email, :username, :password, :permlevel)", {
                  'email': mail, 'username': usr, 'password': pw, 'permlevel': perms})
        conn.commit()
        conn.close()
        logger.debug('user added successfully')
        return True
    except Exception as e:
        logger.error('unable to register user {} -> {}', usr, e)
        raise(static.RegistrationError('User registration failed'))
        return False


def get_user(usr, DATABASE='database.db'):
    # TODO: Add documentation for return value type
    '''Get User data from database

    Arguments:
        usr {string} -- Username

    Keyword Arguments:
        DATABASE {string} -- Path to satabase file (default: {'database.db'})

    Returns:
        [type] -- User data
    '''
    create()
    logger.trace(f'finding user details of {usr}')
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=:usr_name",
              {'usr_name': usr})
    fetch = c.fetchone()
    conn.commit()
    conn.close()
    return fetch


def get_pass(usr, DATABASE='database.db'):
    '''Get password (encrypted) for specified user

    Arguments:
        usr {string} -- Username

    Keyword Arguments:
        DATABASE {string} -- Path to database file (default: {'database.db'})

    Returns:
        string -- Encrypted password
    '''
    logger.trace(f'finding password for {usr}')
    if not username_aviable(usr):
        fetch = get_user(usr, DATABASE)
        logger.trace(f'password for user {usr} found: {fetch[2]}')
        return fetch[2]
    else:
        logger.debug(f'password for user {usr} not found: No such user')
        return ''


def get_mail(usr, DATABASE='database.db'):
    '''Get E-Mail Address for specified user

    Arguments:
        usr {string} -- Username

    Keyword Arguments:
        DATABASE {string} -- Path to database file (default: {'database.db'})

    Returns:
        string -- E-Mail Address
    '''
    logger.debug(f'finding email for {usr}')
    fetch = get_user(usr, DATABASE)
    logger.debug(f'email address for {usr} found: {fetch[0]}')
    return fetch[0]


def get_permissions(usr, DATABASE='database.db'):
    # TODO: Add documentation for return value type
    '''Get Permission level of specified user

    Arguments:
        usr {string} -- Username

    Returns:
        [type] -- Permission level
    '''
    logger.debug('finding permission level for {}', usr)
    fetch = get_user(usr, DATABASE)
    permlvl = fetch[3]
    logger.debug('permission level found: {}', permlvl)
    return permlvl


def update_user_permissions(usr, perm, DATABASE='database.db'):
    '''Update permission level of specified user

    Arguments:
        usr {string} -- Username
        perm {string} -- Permission level

    Keyword Arguments:
        DATABASE {string} -- Path to database fle (default: {'database.db'})
    '''
    logger.debug('changing permission level of user {}, to {}', usr, perm)
    # Get database data, to be able to register new user under same data (with changed permission level)
    fetch = get_user(usr)
    # extract database data to multiple vars
    curpermlvl = fetch[3]
    mail = fetch[0]
    pw = fetch[2]

    if int(curpermlvl) > int(perm):
        logger.debug('found user info: (usr: {}, mail: {}, enc-pw: {}, perms: {}) --> ELEVATION to {}',
                     usr, mail, pw, curpermlvl, perm)
    elif int(curpermlvl) < int(perm):
        logger.debug('found user info: (usr: {}, mail: {}, enc-pw: {}, perms: {}) --> DEMOTION to {}',
                     usr, mail, pw, curpermlvl, perm)
    else:
        logger.debug(
            'found user info: (usr: {}, mail: {}, enc-pw: {}, perms: {}) --> PERMS EQUAL')
    # unregister extracted user
    remove_user(usr, DATABASE)
    # register extracted user back, with different permission
    register_user(mail, usr, pw, perm)
    logger.debug('permission level changed successfully')


def username_aviable(usr, DATABASE='database.db'):
    '''Check if specified username is aviable

    Arguments:
        usr {string} -- Username

    Keyword Arguments:
        DATABASE {string} -- Path to database file (default: {'database.db'})

    Returns:
        bool -- Username aviability
    '''
    logger.trace('checking username availability')
    fetch = get_user(usr, DATABASE)
    if type(fetch) == tuple:
        # User found, return False
        logger.trace(f'Username {usr} taken')
        return False
    else:
        # No such user, return True
        # TODO: Match against a list of protected usernames ('admin', 'dev', '', etc..)
        return True
    logger.trace(f'Username {usr} available')


def account_exists(usr, pw, DATABASE='DATABASE.db'):
    '''Check if there is an account with specified Username and Password

    Arguments:
        usr {string} -- Username
        pw {string} -- Encrypted Password

    Returns:
        bool -- Account Exists
    '''
    logger.trace('verifying username and password for logging-in')

    if not username_aviable(usr):
        pword = get_pass(usr)
        if pword == pw:
            logger.trace(f'user verification confirmed (name: {usr})')
            return True
        else:
            logger.debug(f'user verification failed (name: {usr})')
            return False
    else:
        logger.debug(f'user verification failed (name: {usr})')
        return False


def create_default_user(enabled=True, pword='admin', DATABASE='database.db'):
    if enabled:
        if username_aviable('admin', DATABASE) is True:
            register_user('None set', 'admin',
                          static.encrypt(pword), 1, DATABASE)
