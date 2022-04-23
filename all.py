import locale
import os

from rich.pretty import pprint as print

if os.name != 'posix':
    import ctypes

    import win32api
    import win32con
    import win32file

    for drive in win32api.GetLogicalDriveStrings().split("\x00"):
        type = win32file.GetDriveType(drive)
        if type == win32con.DRIVE_FIXED:
            if win32api.GetVolumeInformation(drive)[0] == "Windows":
                bd = drive
                break

    cflop = [
        fr"{os.getcwd()}\config.yml",
        drive + fr"Users\{os.getenv('username')}\AppData\Roaming\Hyaku\config.yml"
    ]
    lc = locale.windows_locale[ctypes.windll.kernel32.GetUserDefaultUILanguage()][:2]
    cos = 0
    print(os.environ.get("USERPROFILE"))
else:
    cflop = [
        f"{os.getcwd()}/config.yml",
        "~/.config/hyaku/config.yml",
        "~/.hyk",
        "/etc/hyaku/config.yml"
    ]
    if xch:=os.environ.get('XDG_CONFIG_HOME'):
        cflop.insert(1, f"{xch}/hyaku/config.yml")
    lc = locale.getdefaultlocale()[0][:2]
    cos = 1

print(cflop)
print(lc)