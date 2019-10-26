from pathlib import Path
from importlib import import_module
import sqlite3


logger = import_module('RegSys').logger


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
    logger.debug('finding user {} details to change permission level', usr)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=:usr_name",
              {'usr_name': usr})
    fetch = c.fetchone()
    conn.commit()
    conn.close()
    return fetch


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
    logger.debug(
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
        return False


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
