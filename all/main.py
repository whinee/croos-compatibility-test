import locale
import os
from sys import platform as PLATFORM

if os.name == 'posix':
    POSIX = True
else:
    POSIX = False

match PLATFORM:
    case 'win32':
        import ctypes

        LOCALE = locale.windows_locale[ctypes.windll.kernel32.GetUserDefaultUILanguage()][:2]
    case 'darwin' | 'linux':
        if _LOCALE := locale.getdefaultlocale()[0]:
            LOCALE = _LOCALE[:2]
        else:
            LOCALE = 'en'
    case _:
        print(f'Platform not Supported: {PLATFORM}')

print(PLATFORM)
print(LOCALE)