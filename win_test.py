import win32api
import win32file

for drive in win32api.GetLogicalDriveStrings().split("\x00"):
	type = win32file.GetDriveType(drive)
	if type == win32con.DRIVE_FIXED:
		print([drive, win32api.GetVolumeInformation(drive)])
