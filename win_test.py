import win32api

for drive in win32api.GetLogicalDriveStrings().split("\x00"):
		type = win32file.GetDriveType(drive)
    print(type)
		if type == win32con.DRIVE_FIXED:
			print(win32api.GetVolumeInformation(drive))
