#!/bin/env python
#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys, os, os.path
import platform

def show_error_dialog_non_wx(text, title):
	txt = "Please report this crash to developers and attach the following files:\n"
	txt += "\n\t[Documents/Rigs of Rods Toolkit 0.38/logs/Ogre.log]"
	txt += "\n\t[Documents/Rigs of Rods Toolkit 0.38/logs/editor.log]"
	txt += "\n\n ------------------------------------------------------------------------"
	txt += "\n\nError message: \n"
	txt += str(text)
	show_dialog_non_wx(txt, title)


def show_dialog_non_wx(text, title):
    """
    Shows error popup without using any dependencies, if any method is available
    """
    # TODO: Other platforms
    if sys.platform in ['win32', 'win64']:
		try:
			import ctypes  # Built-in library
		except:
			print("Failed to import <ctypes> - not showing Win32 error dialog. Message:", sys.exc_info()[1])
		
		try:
			ctypes.windll.user32.MessageBoxA(0, str(text), str(title), 0)
		except:
			print("Failed to show Win32 error dialog via <ctypes>. Message:", sys.exc_info()[1])       
    

def main():
	"""
	main method
	"""
	has_error_occured = False
	try:
		if sys.platform in ['linux', 'linux2']:
			sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib_common"))
			sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib_linux"))
			binaryRoR = 'RoR.bin'
		elif sys.platform in ['win32', 'win64']:
			#Lepes: use our wx version instead system installed one (avoid user to install it).
			sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib_common"))
			sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib_windows"))
			binaryRoR = 'RoR.exe'
			
		os.chdir(os.path.dirname(__file__))
		from toolkit_exceptions import ToolkitError
		
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
	
	except ToolkitError as err:
		show_dialog_non_wx(err, "Failed to start RoRToolkit")
		has_error_occured = True
	except:
		show_error_dialog_non_wx(sys.exc_info()[1], "Failed to start RoRToolkit")
		has_error_occured = True
	
	if has_error_occured == False:	
		try:
			roreditor.MainFrame.startApp(MainApp)
		except ToolkitError:
			show_dialog_non_wx(str(sys.exc_info()[1]), "RoRToolkit stopped on error")
		except:
			show_error_dialog_non_wx(sys.exc_info()[1], "RoRToolkit crashed :(")		


if __name__ == "__main__": 
	main()
	
