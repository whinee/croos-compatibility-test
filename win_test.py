import win32api

for drive in win32api.GetLogicalDriveStrings().split("\x00"):
	print(win32api.GetVolumeInformation(drive))
