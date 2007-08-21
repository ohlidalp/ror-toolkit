#!/bin/env python
#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys, os, os.path

def main():
	"""
	main method
	"""
	rorexecutable = ''
	if sys.platform in ['linux', 'linux2']:
		sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib_common"))
		sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib_linux"))
		rorexecutable = "RoR.bin"
	elif sys.platform in ['win32']:
		sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib_common"))
		sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib_windows"))
		rorexecutable = "RoR.exe"

	import ror.rorcommon
	if not ror.rorcommon.checkRoRDirectory():
		import ror.starter
		ror.starter.startApp()

	# Import Psyco if available
	try:
		import psyco
		psyco.full()
	except ImportError:
		pass

	import roreditor.MainFrame
	roreditor.MainFrame.startApp()


if __name__=="__main__":
	main()