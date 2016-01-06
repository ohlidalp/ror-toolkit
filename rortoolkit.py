#!/bin/env python
#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys, os, os.path
import platform



def main():
	"""
	main method
	"""	
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
	import wx
	MainApp = wx.PySimpleApp(0) 
	wx.InitAllImageHandlers() #you may or may not need this 
	try:
#	import psyco
		#psyco.full()
		print 'Toolkit need psyco to run: Got It'
	except ImportError:
		print 'Toolkit need psyco to run: Faild to Run'	
	import ror.settingsManager
	# initialize rorSettings Singleton pattern, fulfill standardspaths and initialize logger  
	ror.settingsManager.rorSettings().rorExecutable = binaryRoR
#	ror.settingsManager.rorSettings().onlyParseTrucks = True
	import ror.logger
	ror.settingsManager.rorSettings().onlyParseTrucks = False
	import roreditor.MainFrame
	roreditor.MainFrame.startApp(MainApp) 


if __name__ == "__main__": 
	main()
	
