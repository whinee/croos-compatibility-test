import win32api

for drive in win32api.GetLogicalDriveStrings().split("\x00"):
	try:
		print([drive, win32api.GetVolumeInformation(drive)])
	except Exception as e:
		print(e)
