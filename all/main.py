import locale
import os
import platform

OS_NAME = platform.system()

if os.name != 'posix':
    import ctypes

    POSIX = False
    LOCALE = locale.windows_locale[ctypes.windll.kernel32.GetUserDefaultUILanguage()][:2]
else:
    POSIX = True
    if _LOCALE := locale.getdefaultlocale()[0]:
        LOCALE = _LOCALE[:2] # type: ignore[misc, no-redef]

print(OS_NAME)
print(POSIX)
print(LOCALE)