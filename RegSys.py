from loguru import logger
import main.static as static
import main.database as database
import main.interface as interface


# Path to user database
DATABASE = 'database.db'
LOG_FILE = 'logs/logfile.log'

see_logs = True
create_default_user = True


static.ensure_dir(LOG_FILE)

if see_logs:
    logger.level('TRACE')

logger.add(LOG_FILE, level='TRACE', format='<green>{time: YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level>  | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>',
           filter=None, colorize=None, serialize=False, backtrace=True, diagnose=True, enqueue=False, catch=True)


def logged_in(usr):
    """User-side for Logged-In"""
    choice = usr.show_menu(get_inputs=True)
    returndict = {
        'logout': main,
        'passchange': usr.change_password,
        'mailchange': usr.change_mail,
        'edituser': usr.edit_user,
        'removeuser': usr.remove_user,
        'createuser': usr.create_user,
        'devshell': interface.dev_shell
    }
    returndict[choice]()

    logged_in(usr)


@logger.catch
def main():
    """Main User-Side Interface-"""
    logger.trace('main interface')
    prompt = interface.welcome_screen()
    if prompt == '2':
        # Register
        logger.debug('choice: register (2)')
        usr = interface.user_register()
        if usr:
            logged = interface.user_login(usr=usr.username)
            if logged:
                logged_in(logged)
            else:
                main()
        else:
            main()
    elif prompt == '1':
        # Log In
        logger.debug('choice: login (1)')
        usr = interface.user_login()
        if usr:
            logged_in(usr)
        else:
            main()
    elif prompt == '*':
        interface.handle_exit()
        exit()
    else:
        # Wrong option
        logger.debug(f'choice: invalid ({prompt})')
        interface.invalid_choice()
        main()


if __name__ == '__main__':
    logger.info('Program started directly')
    try:
        database.create_default_user(create_default_user)
        main()
    except Exception as e:
        logger.exception('-Main exception-')
        logger.critical(f'Program Failed: {e}')
        interface.handle_exception(e)
        main()
else:
    logger.info('Program started non-directly')
