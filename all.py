import locale
import os

from rich.pretty import pprint as print

if os.name != 'posix':
    import ctypes

    cflop = [
        fr"{os.getcwd()}\config.yml",
        fr"{os.getenv('USERPROFILE')}\AppData\Roaming\Hyaku\config.yml"
    ]
    lc = locale.windows_locale[ctypes.windll.kernel32.GetUserDefaultUILanguage()][:2]
    cos = 0
else:
    cflop = [
        f"{os.getcwd()}/config.yml",
        "~/.config/hyaku/config.yml",
        "~/.hyk",
        "/etc/hyaku/config.yml"
    ]
    if xch:=os.getenv('XDG_CONFIG_HOME'):
        cflop.insert(1, f"{xch}/hyaku/config.yml")
    lc = locale.getdefaultlocale()[0][:2]
    cos = 1

print(cflop)
print(lc)