
def is_system_windows():
	"""
	Returns True if we're running on windows.
	"""
	import sys
	return sys.platform == "win32" # It's always win32, even on 64bit Python: http://stackoverflow.com/a/2145582 

def list_ror_home_directories():
	"""
	Lists all available RoR home-directories.
	:returns: List of tuples (dirname, full_path)
	"""
	
	import wx
	wx_paths = wx.StandardPaths.Get()
	
	import os.path	
	base_path = wx_paths.GetDocumentsDir()
	all_files = os.listdir(base_path)
	ror_dirs = [] # Tuples (dirname, fullpath)
	for dirname in all_files:
		fullpath = os.path.join(base_path, dirname)
		if os.path.isdir(fullpath):
			dirname_low = dirname.lower();
			if ("rigs of rods" in dirname_low) and ("toolkit" not in dirname_low):
				tup = (dirname, fullpath)
				ror_dirs.append(tup)
	return ror_dirs
				