from pathlib import Path
from importlib import import_module
import sqlite3


logger = import_module('RegSys').logger


def create_database(DATABASE='database.db'):
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


def get_tables(DATABASE='database.db'):
    """Will return all saved info"""
    logger.debug('Accessing all database tables')
    create_database()
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    data = c.fetchall()
    conn.commit()
    conn.close()
    logger.debug('Database tables returned, data: {}', data)
    return data


def delete_table(DATABASE='database.db'):
    logger.info('removing whole database table')
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM users")
    conn.commit()
    conn.close()
    logger.debug('Whole database was deleted')


def remove(usr, DATABASE='database.db'):
    logger.info('removing user {} from database', usr)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username=:usr_name", {'usr_name': usr})
    conn.commit()
    conn.close()
    logger.debug('user removed')


def get_data(usr, DATABASE='database.db'):
    create_database()
    logger.debug('finding user {} details to change permission level', usr)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=:usr_name",
              {'usr_name': usr})
    fetch = c.fetchone()
    conn.commit()
    conn.close()
    return fetch


def file_register(mail, usr, pw, perms, DATABASE='database.db'):
    """Register new user into database file"""
    logger.debug(
        'adding user to database - mail: {} ; usr: {} ; enc_pwd: {} ; perms: {}', mail, usr, pw, perms)
    try:
        create_database()
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


def change_perm_level(usr, perm, DATABASE='database.db'):
    """Change permission level of specified user"""
    logger.debug('changing permission level of user {}, to {}', usr, perm)
    # Get database data, to be able to register new user under same data (with changed permission level)
    fetch = get_data(usr)
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
        return None
    # unregister extracted user
    remove(usr, DATABASE)
    # register extracted user back, with different permission
    file_register(mail, usr, pw, perm)
    logger.debug('permission level changed successfully')
