#!/bin/env python
#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys, os, os.path
import platform

def show_error_dialog_non_wx(text, title):
	txt = "Please report this crash to developers and attach the following files:\n"
	txt += "\n\t[Documents/Rigs of Rods Toolkit 0.38/logs/Crash.log]"
	txt += "\n\t[Documents/Rigs of Rods Toolkit 0.38/logs/Ogre.log] (if present)"
	txt += "\n\t[Documents/Rigs of Rods Toolkit 0.38/logs/editor.log] (if present)"
	txt += "\n\n ------------------------------------------------------------------------"
	txt += "\n\nError message: \n"
	txt += str(text)
	show_dialog_non_wx(txt, title)


def show_dialog_non_wx(text, title):
    """
    Shows error popup without using any dependencies, if any method is available
    """
    # TODO: Other platforms
    if sys.platform == "win32": # Windows 32/64 => always 'win32'
		try:
			import ctypes  # Built-in library
		except:
			print("Failed to import <ctypes> - not showing Win32 error dialog. Message:", sys.exc_info()[1])
		
		try:
			ctypes.windll.user32.MessageBoxA(0, str(text), str(title), 0)
		except:
			print("Failed to show Win32 error dialog via <ctypes>. Message:", sys.exc_info()[1])       
    

def write_crash_log_file():
	import sys, traceback
	
	err = traceback.format_exc()
	separator = "========================================"
	separator += separator
	separator =  "\n" + separator + "\n"
	text = separator + err + separator
	sys.stderr.write(text)
	
	if "win32" in sys.platform:
		# Quick hack to get at least SOME crash-reporting.
		try:
			
			homedir = os.path.expanduser("~/Documents/Rigs of Rods toolkit 0.38") # This is currently hardcoded anyway...
			if not os.path.exists(homedir):
				os.mkdir(homedir)
			logs_dir = homedir + "/logs"
			if not os.path.exists(logs_dir):
				os.mkdir(logs_dir)
		
			crashlog_path = logs_dir + "/Crash.log"
			f = open(crashlog_path, mode='w')
			f.write(text)
			f.close()
		except:
			pass


def main():
	"""
	main method
	"""
	has_error_occured = False
	try:
		sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "source"))
		if sys.platform in ['linux', 'linux2']:
			sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "linux"))
			binaryRoR = 'RoR.bin'
		elif sys.platform in ['win32', 'win64']:
			#Lepes: use our wx version instead system installed one (avoid user to install it).
			sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "windows"))
			binaryRoR = 'RoR.exe'
			
		os.chdir(os.path.dirname(__file__))
		import rortoolkit.exceptions
		
		# Import WxPython GUI library
		import wx
		
		MainApp = wx.PySimpleApp(0) 
		wx.InitAllImageHandlers() #you may or may not need this 	
		import ror.settingsManager
		# initialize rorSettings Singleton pattern, fulfill standardspaths and initialize logger  
		ror.settingsManager.rorSettings().rorExecutable = binaryRoR
		import ror.logger
		ror.settingsManager.rorSettings().onlyParseTrucks = False
		import roreditor.MainFrame
	
	except rortoolkit.exceptions.ToolkitError as err:
		show_dialog_non_wx(err, "Failed to start RoRToolkit")
		write_crash_log_file()
		has_error_occured = True
	except:
		show_error_dialog_non_wx(sys.exc_info()[1], "Failed to start RoRToolkit")
		write_crash_log_file()
		has_error_occured = True
	
	if has_error_occured == False:	
		try:
			roreditor.MainFrame.startApp(MainApp)
		except rortoolkit.exceptions.ToolkitError:
			show_dialog_non_wx(str(sys.exc_info()[1]), "RoRToolkit stopped on error")
			write_crash_log_file()
		except:
			write_crash_log_file()
			show_error_dialog_non_wx(sys.exc_info()[1], "RoRToolkit crashed :(")
			


if __name__ == "__main__": 
	main()
	
