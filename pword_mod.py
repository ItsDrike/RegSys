import sys


def get_pword(prompt='Password: '):
    # Linux case:
    if sys.platform == "linux" or sys.platform == "linux2":
        from getpass import getpass
        password = getpass(f'{prompt}: ')

    # Windows case:
    elif sys.platform == "win32":
        def win_getpass(prompt='Password: ', stream=None):
            """Prompt for password with echo off, using Windows getch()."""
            if sys.stdin is not sys.__stdin__:
                return fallback_getpass(prompt, stream)
            import msvcrt
            for c in prompt:
                msvcrt.putwch(c)
            pw = ""
            while 1:
                c = msvcrt.getwch()
                if c == '\r' or c == '\n':
                    break
                if c == '\003':
                    raise KeyboardInterrupt
                if c == '\b':
                    if pw == '':
                        pass
                    else:
                        pw = pw[:-1]
                        msvcrt.putwch('\b')
                        msvcrt.putwch(" ")
                        msvcrt.putwch('\b')
                else:
                    pw = pw + c
                    msvcrt.putwch("*")
            msvcrt.putwch('\r')
            msvcrt.putwch('\n')
            return pw

        password = win_getpass(f'{prompt}')

    return password
